package paos

import "time"

type Config struct {
	RuntimeDir   string    `yaml:"runtime_dir"`
	WorktreeRoot string    `yaml:"worktree_root"`
	LLM          LLMConfig `yaml:"llm"`
}

type LLMConfig struct {
	BaseURL   string `yaml:"base_url"`
	Model     string `yaml:"model"`
	APIKeyEnv string `yaml:"api_key_env"`
}

type Artifact struct {
	Path           string
	RelPath        string
	Type           string
	Title          string
	Status         string
	Category       string
	ApprovalState  string
	ParentRefs     []string
	ApprovalRefs   []string
	SourceRefs     []string
	RuntimeLogRefs []string
}

type ScanResult struct {
	Artifacts          []Artifact
	Warnings           []string
	DraftOpportunities []Artifact
	StatusCounts       map[string]int
	TypeCounts         map[string]int
}

type ExecutionSpec struct {
	ExecutionWorkspace ExecutionWorkspace `json:"execution_workspace" yaml:"execution_workspace"`
	CommandList        []CommandSpec      `json:"command_list" yaml:"command_list"`
	EnvProfile         EnvProfile         `json:"env_profile" yaml:"env_profile"`
	NetworkIntent      NetworkIntent      `json:"network_intent" yaml:"network_intent"`
	PrivateRuntimeLog  PrivateRuntimeLog  `json:"private_runtime_log" yaml:"private_runtime_log"`
}

type ExecutionWorkspace struct {
	Repo         string `json:"repo" yaml:"repo"`
	Mode         string `json:"mode" yaml:"mode"`
	WorktreeRoot string `json:"worktree_root,omitempty" yaml:"worktree_root,omitempty"`
}

type CommandSpec struct {
	ID          string         `json:"id" yaml:"id"`
	Command     string         `json:"command" yaml:"command"`
	AllowedArgs map[string]any `json:"allowed_args,omitempty" yaml:"allowed_args,omitempty"`
	Repeatable  bool           `json:"repeatable" yaml:"repeatable"`
}

type EnvProfile struct {
	Mode  string   `json:"mode" yaml:"mode"`
	Allow []string `json:"allow" yaml:"allow"`
}

type NetworkIntent struct {
	Enabled bool   `json:"enabled" yaml:"enabled"`
	Reason  string `json:"reason" yaml:"reason"`
}

type PrivateRuntimeLog struct {
	Storage   string `json:"storage" yaml:"storage"`
	Retention string `json:"retention" yaml:"retention"`
	Redaction string `json:"redaction" yaml:"redaction"`
}

type DraftResponse struct {
	Title         string        `json:"title"`
	Goal          string        `json:"goal"`
	ExecutionSpec ExecutionSpec `json:"execution_spec"`
	Risks         []string      `json:"risks,omitempty"`
	SourceRefs    []string      `json:"source_refs,omitempty"`
	Comments      []string      `json:"comments,omitempty"`
}

type LLMPayload struct {
	Mode              string
	ParentPath        string
	ParentArtifact    Artifact
	ParentBody        string
	ContextPack       []ContextPackItem
	ContextSummary    string
	ADRSummaries      map[string]string
	RuntimeTaskTmpl   string
	ResultSummary     string
	RuntimeLogRefs    []string
	ExcludedDataNotes []string
}

type ContextPackItem struct {
	Ref       string
	Path      string
	Status    string
	Reason    string
	Source    string
	Bytes     int
	Truncated bool
	Content   string
}

type RunLog struct {
	TaskPath        string    `json:"task_path"`
	CommandID       string    `json:"command_id"`
	Command         string    `json:"command"`
	Worktree        string    `json:"worktree"`
	StartedAt       time.Time `json:"started_at"`
	EndedAt         time.Time `json:"ended_at"`
	ExitCode        int       `json:"exit_code"`
	Stdout          string    `json:"stdout"`
	Stderr          string    `json:"stderr"`
	EnvProfileMode  string    `json:"env_profile_mode"`
	AllowedEnvNames []string  `json:"allowed_env_names"`
}
