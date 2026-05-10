# Use Runtime Tasks As Execution Requests

The Personal Agent OS Runtime will execute task-scoped Runtime Task artifacts rather than executing Issues directly. A Runtime Task is a child execution request for a parent Issue or Plan, lives under `.scratch/<feature>/runtime-tasks/<NN>-<slug>.md`, and carries the explicit command list, execution workspace, environment profile, network intent, log policy, and approval references needed by the Runtime.
