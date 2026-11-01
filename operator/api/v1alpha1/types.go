package v1alpha1

import (
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/apimachinery/pkg/runtime/schema"
	"sigs.k8s.io/controller-runtime/pkg/scheme"
)

// ==========================================
// 1. API Group & Scheme Registration
// ==========================================

var (
	// GroupVersion is the group and version for this API (autoscaling.minorproject.io/v1alpha1)
	GroupVersion = schema.GroupVersion{Group: "autoscaling.minorproject.io", Version: "v1alpha1"}

	// SchemeBuilder registers our custom Go types with the Kubernetes API runtime
	SchemeBuilder = &scheme.Builder{GroupVersion: GroupVersion}

	// AddToScheme adds the types in this group-version to any runtime.Scheme
	AddToScheme = SchemeBuilder.AddToScheme
)

func init() {
	SchemeBuilder.Register(&PredictiveAutoscaler{}, &PredictiveAutoscalerList{})
}

// ==========================================
// 2. Custom Resource Definition (CRD) Types
// ==========================================

// PredictiveAutoscalerSpec defines the desired user configuration
type PredictiveAutoscalerSpec struct {
	// TargetDeployment is the name of the Kubernetes Deployment to scale
	TargetDeployment string `json:"targetDeployment"`

	// PredictionURL is the HTTP URL of the Python ML forecast service
	// Example: "http://127.0.0.1:8000/api/v1/forecast/demo-app"
	PredictionURL string `json:"predictionURL"`

	// MinReplicas is the minimum pod count allowed (lower safety limit)
	MinReplicas int32 `json:"minReplicas"`

	// MaxReplicas is the maximum pod count allowed (upper safety limit)
	MaxReplicas int32 `json:"maxReplicas"`

	// PollIntervalSeconds is the polling frequency in seconds to query the ML model
	PollIntervalSeconds int32 `json:"pollIntervalSeconds,omitempty"`
}

// PredictiveAutoscalerStatus defines the observed live state
type PredictiveAutoscalerStatus struct {
	// CurrentReplicas is the current replica count of the target deployment
	CurrentReplicas int32 `json:"currentReplicas,omitempty"`

	// DesiredReplicas is the last computed target replica count
	DesiredReplicas int32 `json:"desiredReplicas,omitempty"`

	// LastPredictedDemand is the last demand value (req/s) from the ML model
	LastPredictedDemand float64 `json:"lastPredictedDemand,omitempty"`

	// LastScaleTime is the timestamp when the deployment was last scaled
	LastScaleTime *metav1.Time `json:"lastScaleTime,omitempty"`

	// Message gives a human-readable status description
	Message string `json:"message,omitempty"`
}

// +kubebuilder:object:root=true
// +kubebuilder:subresource:status

// PredictiveAutoscaler is the top-level Custom Resource object
type PredictiveAutoscaler struct {
	metav1.TypeMeta   `json:",inline"`
	metav1.ObjectMeta `json:"metadata,omitempty"`

	Spec   PredictiveAutoscalerSpec   `json:"spec,omitempty"`
	Status PredictiveAutoscalerStatus `json:"status,omitempty"`
}

// +kubebuilder:object:root=true

// PredictiveAutoscalerList contains a list of PredictiveAutoscaler
type PredictiveAutoscalerList struct {
	metav1.TypeMeta `json:",inline"`
	metav1.ListMeta `json:"metadata,omitempty"`
	Items           []PredictiveAutoscaler `json:"items"`
}

// ==========================================
// 3. Kubernetes Runtime DeepCopy Methods
// ==========================================

func (in *PredictiveAutoscaler) DeepCopyInto(out *PredictiveAutoscaler) {
	*out = *in
	out.TypeMeta = in.TypeMeta
	in.ObjectMeta.DeepCopyInto(&out.ObjectMeta)
	out.Spec = in.Spec
	in.Status.DeepCopyInto(&out.Status)
}

func (in *PredictiveAutoscaler) DeepCopy() *PredictiveAutoscaler {
	if in == nil {
		return nil
	}
	out := new(PredictiveAutoscaler)
	in.DeepCopyInto(out)
	return out
}

func (in *PredictiveAutoscaler) DeepCopyObject() runtime.Object {
	if c := in.DeepCopy(); c != nil {
		return c
	}
	return nil
}

func (in *PredictiveAutoscalerList) DeepCopyInto(out *PredictiveAutoscalerList) {
	*out = *in
	out.TypeMeta = in.TypeMeta
	in.ListMeta.DeepCopyInto(&out.ListMeta)
	if in.Items != nil {
		in, out := &in.Items, &out.Items
		*out = make([]PredictiveAutoscaler, len(*in))
		for i := range *in {
			(*in)[i].DeepCopyInto(&(*out)[i])
		}
	}
}

func (in *PredictiveAutoscalerList) DeepCopy() *PredictiveAutoscalerList {
	if in == nil {
		return nil
	}
	out := new(PredictiveAutoscalerList)
	in.DeepCopyInto(out)
	return out
}

func (in *PredictiveAutoscalerList) DeepCopyObject() runtime.Object {
	if c := in.DeepCopy(); c != nil {
		return c
	}
	return nil
}

func (in *PredictiveAutoscalerSpec) DeepCopyInto(out *PredictiveAutoscalerSpec) {
	*out = *in
}

func (in *PredictiveAutoscalerSpec) DeepCopy() *PredictiveAutoscalerSpec {
	if in == nil {
		return nil
	}
	out := new(PredictiveAutoscalerSpec)
	in.DeepCopyInto(out)
	return out
}

func (in *PredictiveAutoscalerStatus) DeepCopyInto(out *PredictiveAutoscalerStatus) {
	*out = *in
	if in.LastScaleTime != nil {
		in, out := &in.LastScaleTime, &out.LastScaleTime
		*out = (*in).DeepCopy()
	}
}

func (in *PredictiveAutoscalerStatus) DeepCopy() *PredictiveAutoscalerStatus {
	if in == nil {
		return nil
	}
	out := new(PredictiveAutoscalerStatus)
	in.DeepCopyInto(out)
	return out
}

