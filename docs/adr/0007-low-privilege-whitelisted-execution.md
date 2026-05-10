# Use Low-Privilege Whitelisted Execution

Runtime command execution will require a low-privilege execution identity such as `agentos_runner` plus explicit workspace, command, environment, timeout, and approval boundaries. A low-privilege user alone is not enough: destructive commands, unapproved scripts, broad network access, and credential exposure must also be constrained by policy and tool boundaries.
