# Day 2 Printable Sensor and Line Template

[Download the A4 PDF](day02-line-templates.pdf).

Three alternatives are provided. Print **one selected page per student**, single-sided:

| PDF page | Stripe width | Use |
|---|---|---|
| 1 | 10 mm | Initial candidate |
| 2 | 6 mm | Narrower alternative |
| 3 | 14 mm | Wider alternative |

Use A4 portrait, **Actual size / 100%**. Disable Fit/Shrink to page and verify that the printed ruler measures 50 mm. The PDF contains vector black shapes on white, with no scaling-dependent raster line edges. Print a trial copy and check actual sensor response before producing the class set.

Each page has two 35 mm calibration patches, a 160 mm long central stripe, and an 80 mm wide by 15 mm deep stop bar at its upper end. The black patch is for measuring an individual sensor. Check whether the stop bar spans both sensing spots on the actual robot.

For the existing relay algorithm, choose a stripe narrower than the clear gap between the sensing spots, so both see white when centred. Width selection depends on the actual sensor spacing and sensing height; 10 mm is a starting candidate, not a universal requirement.

## Use in class

1. Motor power off: read the centre of each calibration patch at the normal sensor height. Keep labels and borders outside the sensing spots.
2. Check each sensor separately by moving the paper beneath it.
3. With wheels lifted, slide the stripe sideways under the sensors and verify left/right steering commands.
4. Slide the stop bar beneath both sensors and confirm that both-black stops the controller.
5. For a brief floor test, put the sensing spots near the lower end, stripe between them, and point the robot towards the bar. Use the lowest reliable starting duty and check the available distance. The movement examples now have no time limit: stop-at-bar and relay following end on both-black, or use Ctrl+C / the motor-power switch. A single A4 sheet is for a short section, not continuous tracking.

This is a bench exercise and short straight section. It is not a complete line-following course and does not solve the white/white line-loss ambiguity. The page is intentionally free of text around the lower track area. Secure it flat and avoid seams in the sensing path.

The original PDF can be rebuilt with `tools/build_line_templates.py` using ReportLab. The script also creates the identical instructor delivery copy under `output/pdf/`.

More teaching ideas: [additional sensor exercises](../docs/day-02-extra-exercises.md).
