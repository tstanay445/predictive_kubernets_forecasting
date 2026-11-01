package controllers

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"time"

	appsv1 "k8s.io/api/apps/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/apimachinery/pkg/types"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/log"

	autoscalingv1alpha1 "github.com/sahilkukreja/predictive-autoscaler/api/v1alpha1"
)

// ForecastResponse matches the FastAPI response schema in main.py
type ForecastResponse struct {
	TargetWorkload         string  `json:"target_workload"`
	ForecastHorizonSeconds int     `json:"forecast_horizon_seconds"`
	PredictedDemand        float64 `json:"predicted_demand"`
	ConfidenceLower        float64 `json:"confidence_lower"`
	ConfidenceUpper        float64 `json:"confidence_upper"`
	RecommendedReplicas    int32   `json:"recommended_replicas"`
}

// PredictiveAutoscalerReconciler reconciles a PredictiveAutoscaler object
type PredictiveAutoscalerReconciler struct {
	client.Client
	Scheme     *runtime.Scheme
	HTTPClient *http.Client
}

// Reconcile is part of the main kubernetes reconciliation loop which aims to
// move the current state of the cluster closer to the desired state.
func (r *PredictiveAutoscalerReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
	logger := log.FromContext(ctx)

	// 1. Fetch the PredictiveAutoscaler custom resource
	var pa autoscalingv1alpha1.PredictiveAutoscaler
	if err := r.Get(ctx, req.NamespacedName, &pa); err != nil {
		return ctrl.Result{}, client.IgnoreNotFound(err)
	}

	logger.Info("Reconciling PredictiveAutoscaler", "name", pa.Name, "target", pa.Spec.TargetDeployment)

	// Determine poll interval (default 30 seconds)
	pollInterval := time.Duration(pa.Spec.PollIntervalSeconds) * time.Second
	if pollInterval <= 0 {
		pollInterval = 30 * time.Second
	}

	// 2. Fetch the Target Deployment
	var deployment appsv1.Deployment
	deployKey := types.NamespacedName{
		Namespace: pa.Namespace,
		Name:      pa.Spec.TargetDeployment,
	}
	if err := r.Get(ctx, deployKey, &deployment); err != nil {
		logger.Error(err, "Target deployment not found", "deployment", pa.Spec.TargetDeployment)
		pa.Status.Message = fmt.Sprintf("Error: target deployment '%s' not found", pa.Spec.TargetDeployment)
		_ = r.Status().Update(ctx, &pa)
		return ctrl.Result{RequeueAfter: pollInterval}, nil
	}

	// 3. Query the FastAPI ML Service for Forecast
	forecast, err := r.fetchForecast(pa.Spec.PredictionURL)
	if err != nil {
		logger.Error(err, "Failed to fetch prediction from ML service", "url", pa.Spec.PredictionURL)
		pa.Status.Message = fmt.Sprintf("Warning: ML service unreachable: %v", err)
		_ = r.Status().Update(ctx, &pa)
		return ctrl.Result{RequeueAfter: 10 * time.Second}, nil
	}

	logger.Info("Received ML Forecast",
		"predictedDemand", forecast.PredictedDemand,
		"recommendedReplicas", forecast.RecommendedReplicas,
	)

	// 4. Apply Safety Guardrails (FR-11: Min/Max replica clamp)
	desiredReplicas := forecast.RecommendedReplicas
	if desiredReplicas < pa.Spec.MinReplicas {
		desiredReplicas = pa.Spec.MinReplicas
	}
	if desiredReplicas > pa.Spec.MaxReplicas {
		desiredReplicas = pa.Spec.MaxReplicas
	}

	// 5. Compare current replicas with desired replicas and scale if needed
	currentReplicas := int32(1)
	if deployment.Spec.Replicas != nil {
		currentReplicas = *deployment.Spec.Replicas
	}

	if currentReplicas != desiredReplicas {
		logger.Info("Proactively scaling deployment",
			"deployment", deployment.Name,
			"currentReplicas", currentReplicas,
			"desiredReplicas", desiredReplicas,
			"predictedDemand", forecast.PredictedDemand,
		)

		deployment.Spec.Replicas = &desiredReplicas
		if err := r.Update(ctx, &deployment); err != nil {
			logger.Error(err, "Failed to update deployment replicas", "deployment", deployment.Name)
			pa.Status.Message = fmt.Sprintf("Error updating deployment: %v", err)
			_ = r.Status().Update(ctx, &pa)
			return ctrl.Result{RequeueAfter: 5 * time.Second}, nil
		}

		now := metav1.Now()
		pa.Status.LastScaleTime = &now
	}

	// 6. Update Status
	pa.Status.CurrentReplicas = deployment.Status.Replicas
	pa.Status.DesiredReplicas = desiredReplicas
	pa.Status.LastPredictedDemand = forecast.PredictedDemand
	pa.Status.Message = fmt.Sprintf("Demand: %.1f req/s -> Replicas: %d (Healthy)", forecast.PredictedDemand, desiredReplicas)

	if err := r.Status().Update(ctx, &pa); err != nil {
		logger.Error(err, "Failed to update PredictiveAutoscaler status")
		return ctrl.Result{RequeueAfter: pollInterval}, nil
	}

	return ctrl.Result{RequeueAfter: pollInterval}, nil
}

// fetchForecast queries the FastAPI prediction service
func (r *PredictiveAutoscalerReconciler) fetchForecast(url string) (*ForecastResponse, error) {
	client := r.HTTPClient
	if client == nil {
		client = &http.Client{Timeout: 5 * time.Second}
	}

	resp, err := client.Get(url)
	if err != nil {
		return nil, fmt.Errorf("GET %s failed: %w", url, err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("unexpected status %d from %s", resp.StatusCode, url)
	}

	var forecast ForecastResponse
	if err := json.NewDecoder(resp.Body).Decode(&forecast); err != nil {
		return nil, fmt.Errorf("failed to decode forecast response: %w", err)
	}

	return &forecast, nil
}

// SetupWithManager sets up the controller with the Manager.
func (r *PredictiveAutoscalerReconciler) SetupWithManager(mgr ctrl.Manager) error {
	return ctrl.NewControllerManagedBy(mgr).
		For(&autoscalingv1alpha1.PredictiveAutoscaler{}).
		Complete(r)
}
