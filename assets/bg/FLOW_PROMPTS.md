# Google Flow: 16 Background Images

## PROMPT 1: Agent instruction (paste first)

```
You are generating a consistent set of cinematic background images for a long-form storytelling YouTube channel. Follow these rules for EVERY image in this session:

- Photorealistic cinematic still frame, shot on 35mm, shallow depth of field
- Muted desaturated color grading, dim moody lighting, quiet melancholic atmosphere
- Theme: American middle-class family drama, silence, absence, aftermath
- Aspect ratio 16:9 landscape, highest resolution available
- STRICTLY NO people, NO faces, NO body parts, NO text, NO lettering, NO watermarks
- All images must feel like frames from the same film: same grading, same mood, same visual language
```

## PROMPT 2: Execution 1 (10 images, home & family settings)

```
Using the style rules above, generate 10 separate images, one per scene:

1. A dim suburban living room at dusk, rain streaking down the window
2. An empty family dinner table with unfinished meals under a single warm overhead light
3. A rain-covered window at night, blurred city lights glowing beyond the glass
4. A dark hallway lined with framed family photos, one frame hanging tilted
5. A suburban house exterior at night, only one upstairs window lit
6. A worn armchair beside a dim lamp in an otherwise empty room
7. A kitchen at midnight, one light on, two cold cups of coffee on the counter
8. Packed cardboard boxes in an emptied bedroom with a bare mattress
9. A front porch in heavy rain, the front door closed, porch light glowing
10. A dark staircase in a family home, cold light spilling down from the top floor
```

## PROMPT 3: Execution 2 (6 images, story-arena settings)

```
Using the same style rules, generate 6 separate images, one per scene:

1. An empty courtroom with wooden benches, late afternoon light through tall windows
2. A hospital corridor at night, cold fluorescent light, a row of empty chairs
3. A corporate office at night, city skyline through the glass wall, a single desk lamp on
4. A lawyer's desk covered in scattered documents, a fountain pen and reading glasses on top
5. An empty wedding venue after the event, scattered chairs and deflated balloons
6. A long empty highway at dawn, light mist, first sunlight on the horizon
```

## After generating
Save all 16 as jpg/png → drop into `~/Documents/revenge-pipeline/assets/bg/`.
The pipeline picks them up automatically (per-video shuffle already handles variety).
Add more images anytime by dropping new files into the same folder.
