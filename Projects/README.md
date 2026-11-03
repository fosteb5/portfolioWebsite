# Project files

Source files behind the projects on this site. The website itself lives in `src/` and does not build anything from this folder.

## SolarBlimp (LiftLabs)

- `SolidWorks/`: the mounting plate, motor-to-servo mount and GPS enclosure as SolidWorks parts with STL exports, plus the circuit layout drawing.
- `Blender/liftlabs-print.blend`: two scenes rendered for the LiftLabs case study.
  - **LiftLabs** prints the three STL parts layer by layer. Re-render it with the `LL_render.py` text block.
  - **LiftLabs Blimp** is the finished blimp: envelope, fins, four flexible solar panels, and 1 m arms with tilting motors. The `BL_render.py` text block holds `render_web()` for the site's scroll animation and `render_loop()` for the video.
- `Blender/renders/`: `liftlabs-blimp-loop.mp4` (an 8 second loop) and `blimp-hero.jpg`. Frame-by-frame renders are not committed, because the .blend regenerates them.
- Design notes: the power and solar estimates, the bill of materials, the weight values and the control pseudocode.
- `websiteTest/`: an early test of the project website.

The blimp's firmware and team website are in [fosteb5/LiftLabs](https://github.com/fosteb5/LiftLabs).

## VolumeRemote

- `Blender/volume-remote.blend`: the receiver and the motor mount, modelled from `setup-photo.jpg`, so sizes are estimates. The `VR_render.py` text block holds `render_web()` for the site's scroll animation, where the stepper turns the knob and the display counts up, and `render_loop()` for the video.
- `Blender/renders/`: `volume-remote-loop.mp4` (an 8 second loop) and `volume-remote-hero.jpg`.

## Other folders

- `Burbon Dispencer/`: the bill of materials, first sketch and platform design.
- `Camera App/`: a small browser camera app.
- `testing/`: build scripts for a desktop app test.

Application forms that list teammates' and staff contact details are left out.
