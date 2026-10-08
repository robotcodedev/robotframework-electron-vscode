# Spec Delta

## ADDED Requirements

### Requirement: Video recording
`New Electron Application` SHALL record a video of the application's windows when it is given `record_video`. It SHALL store the video in Browser's video folder of the output directory unless `record_video` names a folder, return the video's path in the page details of its return value, and embed the video in the log, as Browser does for `New Context`.

#### Scenario: Video of an application
- **WHEN** a test starts an application with `record_video`, acts in its window and closes it
- **THEN** a video of the window exists at the path in the returned page details, and the log embeds it

#### Scenario: Action overlay
- **WHEN** `record_video` contains `showActions`
- **THEN** the video shows the performed actions

#### Scenario: No recording by default
- **WHEN** a test starts an application without `record_video`
- **THEN** no video is recorded, and the video path in the page details is empty
