# Cinematic reveals and shot revisions

Use this route when the brief calls for a larger world beyond the interface, a second action after the original ending, or a correction to a particular shot. A short interface film can still end on its first payoff.

## Give the next action a consequence

Begin with the last approved frame. Identify what the viewer expects to happen next and which product action can cause it. If the film ends on a new prompt and the user wants to see the result, leave time to read the prompt, visibly press send, then show the result. A product control such as the send arrow can carry the visual joke when animating the brand mark would distort it.

For each new cut, record the outgoing detail, the incoming detail that matches it, and the moment the audience understands the new scale. One worked sequence used a spacecraft dial → a send button, a lunar landscape → a printed poster held by an astronaut, and a spiral galaxy → the next send button. A second send lit a Sun. Its bright edge shrank into the glint in a whale’s eye, and a calf emerged from behind the adult’s fin. Choose imagery that belongs to the brief.

## Build the transition on two anchors

- Plan the crop in square and portrait before generating assets. For a pullback, leave enough image beyond the subject to cover the early zoom and both frames. For an object that reappears as a physical prop, use the actual finished art as the image reference.
- Measure the shared feature in each image as a fraction of its width and height. Position the source around that point. For an unrotated image, its top left is `(screenX − u × drawnWidth, screenY − v × drawnHeight)`. With rotation, translate to the screen anchor, rotate, then draw at the negative local offset. Match apparent size and heading across a moving cut.
- A reflection and a pupil are two different anchors. Lock the Sun to the glint for the first reveal, then measure the pupil’s final screen position for the cut to the animal in profile. Derive it again for the portrait crop.
- For a many-orders-of-magnitude zoom, use intermediate views with recognizable landmarks. Interpolate positive image sizes geometrically. When perspective changes abruptly, cut on a shared landmark or motion cue. Shrinking a rectangular portrait over a wider shot can expose its border and briefly duplicate the subject.
- For a galaxy collapsing into a button, paint the full circular aperture before clipping the star field. Give foreground and background assets separate motion when the action needs depth. A calf can start behind its parent and emerge on its own path. Time an answering sound to the instant it becomes visible.

Keep the existing seekable timeline. If a new ending changes the runtime, update the root, scene, audio clip, animation clock and score together. Keep generated art in the editable project and derive sound cues from the same shot times.

## Review and change one shot

1. Inspect frames just before, at and after each transition, plus the widest view, in both formats. Look for jumps in the anchor, duplicate subjects, exposed plate edges and shapes that read differently at phone size. On a canvas scene the rendered frames are the evidence for drawn content.
2. For screenshot feedback, name the visible issue and make the smallest useful change. In the Sun shot, one large closed prominence read as a handle. Editing the existing plate into several irregular filaments kept the disk’s position and the glint match. A different shot may need a different correction.
3. Re-render the complete cuts. Inspect the changed frames from the encoded MP4s, check video and audio duration with ffprobe, and refresh the editable sources and any delivery preview. For a late revision, a short excerpt starting just before the triggering action lets the user review the fix immediately. Deliver the full film alongside it.
