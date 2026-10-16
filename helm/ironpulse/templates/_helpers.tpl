{{/* Base name: release name, or "<release>-<chart>" when they differ. */}}
{{- define "ironpulse.fullname" -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- if contains $name .Release.Name -}}
{{- .Release.Name | trunc 50 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name $name | trunc 50 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}

{{- define "ironpulse.labels" -}}
app.kubernetes.io/part-of: ironpulse
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
{{- end -}}

{{/* Selector labels for one component (backend / frontend / postgres). */}}
{{- define "ironpulse.selector" -}}
app.kubernetes.io/name: {{ .component }}
app.kubernetes.io/instance: {{ .root.Release.Name }}
{{- end -}}

{{- define "ironpulse.postgresHost" -}}
{{- if .Values.postgres.enabled -}}
{{ include "ironpulse.fullname" . }}-postgres
{{- else -}}
{{ required "postgres.externalHost is required when postgres.enabled=false" .Values.postgres.externalHost }}
{{- end -}}
{{- end -}}

{{- define "ironpulse.podSecurity" -}}
allowPrivilegeEscalation: false
capabilities:
  drop: ["ALL"]
{{- end -}}
