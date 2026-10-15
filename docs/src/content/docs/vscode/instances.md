---
title: Instances, logs and troubleshooting
description: Where each VS Code instance keeps its directories and logs, how earlier runs are cleaned up, and what to check when VS Code misbehaves.
sidebar:
  order: 7
---

[Logs and troubleshooting](../../running/logs/) covers what applies to both libraries. This page adds what is specific to VS Code.

## Instance directories

Every VS Code instance gets its own folder `vscode/<n>` in the output directory, numbered from 1, with its user-data and extensions directories, unless `user_data_dir` or `extensions_dir` of `Start VS Code` give them; VS Code then writes its logs into the given user-data directory. `Execute VS Code CLI Command` with `executable` gets such a folder as well, and `Get VS Code Instance Directories` returns the directories of an instance. The folders stay after the run, so VS Code's own logs can be read afterwards:

- `vscode/<n>/user-data/logs/<timestamp>/main.log` for the main process,
- `vscode/<n>/user-data/logs/<timestamp>/window1/` for the window, with the extension host's log in `exthost/exthost.log`.

When a run starts, the library removes the `vscode` folder that earlier runs left in the same output directory, the way Browser cleans its own output folders. Two runs that use the same output directory at the same time would remove each other's folders, so give parallel runs their own output directories. pabot does that already.

## Troubleshooting

**The command palette runs the wrong command.** The palette filters asynchronously. Wait for the command's row before pressing Enter, as in [the first VS Code test](../getting-started/#first-test).
