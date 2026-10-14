PhotoCraft: map of the New Document flow and a plan for a Photoshop-style redesign. Read-only; nothing was modified and cargo was not run.

All paths are relative to the scratchpad clone at /tmp/claude-0/-home-user/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/photocraft. The user's real checkout at /home/user/photocraft may differ.

Main finding: File > New is already a Photoshop-style dialog. It has category tabs, preset cards, a PRESET DETAILS column, Close and Create buttons, Recent, Saved and Clipboard presets. So the redesign is a reskin and relayout of `crates/ui-egui/src/new_doc_ui.rs` plus a few engine additions. It is not a rewrite.

## 1. Rules that constrain UI, colour, icon and asset work

There is no CLAUDE.md and no ui-guidelines.md. The rules are in AGENTS.md, docs/ui-design.md, docs/contributing.md and ATTRIBUTION.md.

**Clean-room**
- AGENTS.md:64 "Clean-room. We studied Photoshop … for *behaviour and look only*. Never copy their code, shaders, profiles or assets … Third-party assets must be permissively licensed, keep their license file next to them, and get a row in `ATTRIBUTION.md` … so do original assets."
- docs/contributing.md:5 "do not copy code, shaders, icons, ICC profiles or other assets from proprietary software (such as Photoshop). Match behaviour and look by observation and public specs."
- ATTRIBUTION.md:3-7: every non-code asset gets a row in the same change.
- ATTRIBUTION.md:55-57 is the precedent for palettes inspired by another product: it states the colour values are original.

**Tokens and widgets**
- AGENTS.md:66 "UI state lives in `ui-egui/src/state.rs` (serde), so the control channel can read and drive it. Colours and radii come from `theme::Tokens`, never hard-coded."
- docs/ui-design.md:30 "Colours and radii come from tokens. Read them with `Tokens::get(ctx)`; never hard-code a colour in a widget."
- docs/ui-design.md:31: shared widgets live in widgets.rs (`primary_button`/`secondary_button`, `dropdown`, `checkbox`, `hairline`, `elided_label`).
- docs/contributing.md:11 "UI: use `theme::Tokens` and `widgets::*`. Verify visually … attach before/after screenshots."
- docs/ui-design.md:32 "A label never overflows its row … use `widgets::elided_label`."

**Icons**
- docs/ui-design.md:33 "Lucide SVGs in `assets/icons` (ISC licence), embedded via `icon_data.rs`." How to add one: :42-50.
- docs/ui-design.md:91 "Where the font lacks a symbol … draw it with the painter or use a Lucide icon."
- Glyphs drawn with the painter are code, not asset files, so they need no ATTRIBUTION row. A new .svg needs a row and an `icon_data.rs` regeneration.

**Commands**
- AGENTS.md:62 "Everything is a command." UI-only view state goes in `UI_COMMANDS`.
- AGENTS.md:51-60 and :71: never panic; a `run` closure must return Err for any params.
- AGENTS.md:99: run `panic_hunt` when commands change.
- docs/contributing.md:16-26: the add-a-command checklist.

**Verification**
- AGENTS.md:67 "Verify UI changes visually … `--example snapshot` … Look at the PNG."
- docs/ui-design.md:40 "Verify every visual change with `ui.screenshot`, at several window sizes and in every theme."
- AGENTS.md:68: never break wasm.

**Localisation**
- docs/ui-design.md:184-226: English strings are the keys; `tl!` literals are checked.
- A test fails when a `tl!` literal has no entry in a complete catalog: `crates/ui-egui/src/i18n/mod.rs:1114-1157`.
- 20 catalogs are marked complete (`i18n/mod.rs:191-222`).
- docs/ui-design.md:219-220: translations are clean-room, "never from another product's localisation resources".

**Theme facts**
- docs/ui-design.md:7-8: Pro means Spectrum dark #323232 with a #378ef0 accent; Pro Medium is medium grey.
- docs/ui-design.md:22: new installs default to Dark with Pro Medium.
- The `../craftrules` standards (AGENTS.md:3) are not in this clone.

## 2. The current flow

### 2.1 Entry points
All of them open `DialogKind::NewDocument` with `app.new_document_fields()` (`lib.rs:2422-2436`):
- File > New / Cmd+N with no params: `menus.rs:294-296`.
- Home screen "New document…" button: `canvas.rs:2655-2658`.
- Automation `ui.dialog.open {kind:"newDocument", fields?}`: `control.rs:782,845-849`, documented at `docs/control-protocol.md:61`.

### 2.2 Dialog shell (`dialogs.rs`)
- Width is fixed at 800 (min and max): :198-200 and :206-207.
- The title "New Document" (:536) is drawn at :224-234, and the title band drags the dialog.
- The body is `new_doc_ui::body` (:244-248); it returns `true` on a card double-click, which acts as Create.
- The OK label is "Create" and Cancel is "Close" (:364-382), drawn by `widgets::dialog_buttons`.
  - Button order follows the platform (`widgets.rs:1109-1131`).
  - Pro buttons are pills: primary is filled `primary_bg`, secondary is outlined (`widgets.rs:1213-1232`).
  - Labels use `theme::medium(13)` (`widgets.rs:1189`).
- Enter creates (`dialogs.rs:427`) and Esc closes (:458).
- `confirm` (:558-568):
  1. runs `file.new` with `new_doc_ui::command_params(fields)`;
  2. sets `fit_pending`;
  3. on success calls `remember_new_document` (`lib.rs:2366-2370`);
  4. runs `document.recent.add {settings: document_settings(fields)}` on a best-effort basis.
- The modal frame fill is `visuals.window_fill = t.card` (`theme.rs:982`). The Color Picker already overrides its frame (`dialogs.rs:176-178`), which is the precedent for a New Document frame.

### 2.3 State (serde dialog fields, `state.rs:443-448`)
Defaults (`state.rs:1391-1394`): `{name:"Untitled-1", width:1920, height:1080, mode:"rgb", depth:8, background:"white"}`.

Keys sent to `file.new` (anything without a `__` prefix, `new_doc_ui.rs:235-237`): `name`, `width`, `height`, `resolution`, `mode`, `depth`, `background` (white | black | backgroundColor | transparent | #rrggbb), `backgroundColor`.

UI-only keys:

| Key | Purpose |
|---|---|
| `__category` | selected tab (default "Recent") |
| `__preset` | selected built-in card |
| `__savedPreset` | selected saved preset |
| `__unit` | px / in / cm / mm / pt / pica |
| `__resUnit` | in / cm |
| `__orientation` | portrait / landscape |
| `__clipboard` | [w,h] of the clipboard image |
| `__widthTyped`, `__heightTyped` | the value as typed (`shown_size`, :131-153) |
| `__focused` | one-time focus of the name field |
| `__savingPreset`, `__presetName`, `__presetError` | inline save-preset form |
| colour-picker request | opened via `color_picker_ui::request_field` (:755-760) |

Remembered for the next dialog (`lib.rs:2349-2363`): `NEW_DOCUMENT_REMEMBERED` = width, height, resolution, mode, depth, background, `__unit`, `__resUnit`. The validator accepts only numbers and strings.

### 2.4 Presets (`new_doc_ui.rs`)
- `Preset = (name, w px, h px, ppi)` (:16).
- `CATEGORIES` (:19-79), in this order: Recent (Default PhotoCraft Size, HDTV 1080p), Photo (6), Print (8), Art & Illustration (4), Web (5), Mobile (5), Film & Video (5).
- The "Saved" tab is appended last (:504). Photoshop puts it second.
- Bit depths: `DEPTH_OPTIONS` 8 / 16 / 32-float with tooltips (:81). Units: `UNITS` px/in/cm/mm/pt/pica (:84-85).
- A preset of 300 ppi or more is "print" (:172-174).
  - Print presets follow the Units & Rulers Print Resolution and screen presets the Screen Resolution (`at_pref_resolutions`, :208-219).
  - Print presets show the chosen physical unit, or inches (:192-201).
- The orientation toggle turns the presets (`oriented`, :178-188) and swaps W/H including the typed values (`swap_size`, :157-169).
- Changing the resolution keeps the physical size when the unit is physical (`set_resolution`, :242-257).
- Recent tab (`recent_cards`, :400-409): Clipboard card, then up to 20 created documents (`document_preset_cmds.rs:19`), then the defaults not already listed.
  - A recent card's title is the matching built-in name or "Custom" (:373-380).
  - It counts as selected when the dialog's values match it (`holds`, :345-352).
- Saved presets live in `PresetState.documents` and recent ones in `recent_documents` (`engine/src/presets/mod.rs:82-85`). Both persist in the prefs JSON (:136, :155, :191-192).
- The Saved tab is a list of name buttons with Delete buttons (:411-450). The save form is the "Save Preset…" button → Preset Name / Save / Cancel (:452-493). Enter is consumed so it cannot also press Create (:461).
- Cards (:544-603): 164x112, 3 per row, scroll area 3 rows high.
  - Fill `t.field`, hover `t.hover`, selected `t.row_selected` with a 1.5 px `t.accent` outline.
  - Icon: an aspect-ratio rectangle (`page_icon`, :282-286).
  - Title: up to 2 lines, elided (`card_title`, :274-279).
  - Size line: "W x H px @ N ppi" (:383-395).
  - Double-click or triple-click creates (:597).
- Details column (:607-762), 260 px wide, top to bottom:
  1. "PRESET DETAILS";
  2. name TextEdit, focused and selected on open (:612-627);
  3. Width and units dropdown (:633-644);
  4. Height + "Orientation" label (tr_ctx "document") + Lucide rectangle-vertical/rectangle-horizontal buttons (:645-665);
  5. Resolution and Pixels/Inch|Pixels/Centimeter (:667-680);
  6. Color Mode gray/rgb/cmyk/lab and Depth (:682-706);
  7. Background Contents (White/Black/Background Color/Transparent/Custom…) with a 22 px swatch that opens the Color Picker (:708-760);
  8. the save-preset form (:761).

### 2.5 Engine commands (ids and params)
**`file.new`** (`engine/src/commands.rs:401-447`)
- Params doc (:405): `{"width":1..300000=1920, "height":…=1080, "mode":"rgb|gray|grayscale|cmyk|lab"="rgb", "depth":8|16|32=8, "background":"white|black|backgroundColor|transparent|#rrggbb"="white", "backgroundColor":[r,g,b]?, "resolution":1..30000=72, "name":str}`.
- `validate_new_params` (`document_preset_cmds.rs:57-95`) returns "unknown parameter" for any other key (:83). Any new dialog field must therefore be `__`-prefixed or added to the engine first.
- New documents are untagged: `icc_profile: None` (`doc/src/lib.rs:955`).

**Preset commands** (`document_preset_cmds.rs:274-337`)
- `document.presets.list`, `.get`, `.save` and `.delete`; `document.recent.list` and `.add`.
- `DocumentSettings` (:97-111) holds width, height, resolution, mode, depth, background, backgroundColor, unit, resolutionUnit.
- Limits: 256 presets (:18). Duplicates in Recent are detected by comparing `command_params` (:216, :236).

**Commands that exist but are not wired into the dialog**
- `layer.new.artboard` (`artboard_cmds.rs:229-269, 631-637`).
- `edit.assignProfile` with ids `working|srgb|display-p3|adobe-rgb-compat|prophoto-compat|linear-srgb|rec2020|gray-gamma-2.2|sgray|dot-gain-20-compat|lab-d50|coated-cmyk|none` (`color_cmds.rs:908-930, 1138-1145`).
- `edit.profileInfo {}` lists the built-in profiles (`color_cmds.rs:946-950, 1174`).
- Pixel aspect is only a global view option: `ViewOptions.pixel_aspect` (`ui-egui/src/view_cmds.rs:85,117`), presets at :157 and :210-225, menu labels in `menu_catalog.rs:635-644`.

### 2.6 Home / start screen
- `canvas.rs:2627-2683`: a centred column over the canvas dots — "PhotoCraft · open source", subtitle, primary "New document…" and secondary "Open…" (190 px each), drop hint, Recent list (`home_recent`, 6 rows, :2694-2760), Discord and links.
- It has no card fill and paints no background of its own.
- Shown when there are no documents, or toggled from the Home button (`chrome_ui.rs:17-34, 197-206`).

### 2.7 Internationalisation
- Strings are `tl!` literals; the per-category `tl!(name)` and the Recent card title are translated dynamically.
- Orientation uses `tr_ctx(…, "document", "Orientation")` (:653).
- Already in the catalogs: Artboards, Color Profile, Pixel Aspect Ratio, Portrait, Landscape, Clipboard, Custom, Close, Create, Recent, Saved, "BLANK DOCUMENT PRESETS ({n})", "No saved presets yet.", "Save Preset…", "Pixels/Inch", "Custom background color".
- Missing: "Advanced Options".
- Each new `tl!` string needs entries in all 20 `i18n/*.tsv` files.

### 2.8 Tests and how they drive the dialog headlessly
Harness (`new_doc_ui.rs:1010-1537`): an egui_kittest `Harness::build_ui_state` with `dialogs::show` at 1400x900 and Pro theme. Tests open the dialog with `ui.open_dialog(NewDocument, …)` and then:
- find widgets with `get_by_label` and `get_by_role(Role::SpinButton).nth(0|1|2)`, where the order Width, Height, Resolution is assumed (:1187-1190);
- click by hover, drag and drop (:1178-1185);
- locate cards by searching painted `Shape::Text` for the title, because cards have no accessibility label (:1222-1232);
- call `dialogs::confirm` directly, or edit fields and use `set_fields`.

Geometry the tests depend on:
- The Recent heading is "BLANK DOCUMENT PRESETS (3)" and cards are clicked at `heading.left_bottom()+(80,60)` and `+(80+172,60)` (:1405-1411, :1423-1424).
- The Orientation buttons are clicked at `label.right()+gap+12` (:1477-1479, :1491-1493).
- Size lines are matched exactly, e.g. "11.7 x 8.3 in @ 300 ppi", "210 x 297 mm @ 300 ppi" (:1495, :1511, :1518, :933-937).
- The tab labels list is checked (:1526).
- "Save Preset…", "Preset Name", "Save", "Cancel", "Delete", "Saved proof" and "Product square" are found by label (:1086-1137, :1317).
- Card titles must fit 152 px in every language (:882-894).

Other tests:
- Unit tests: :771-1008.
- `new_doc_remember_tests.rs:24-100`.
- `field_tab.rs:184-215` expects exactly one TextInput on open and Tab cycling name → W → H → Resolution → name.
- `state.rs:1458-1466`.
- Engine `document_preset_cmds.rs:341-560` and `engine/tests/panic_hunt.rs`.

### 2.9 Accessibility today
- Buttons from `widgets` carry labels (`widgets.rs:1206`).
- Orientation icon buttons are labelled "Portrait"/"Landscape" through `icons::button` (`icons.rs:174-199`), and the swatch is labelled (`new_doc_ui.rs:748-749`).
- Tabs are clickable Labels with no selected state (:507-509).
- Cards have no label or selected state, and the keyboard cannot reach them: Tab walks text fields only (`dialogs.rs:180`).
- The Width/Height/Resolution captions are plain labels, not linked to their fields; only Preset Name uses `labelled_by` (:464).

### 2.10 Colours the dialog uses now
- Pro Medium (`theme.rs:208-227`): chrome and card #535353, dock #424242, field #454545, tab_strip #4a4a4a, row_selected #6b6b6b, text #eeeeee, text_dim #d4d4d4, text_faint #a0a0a0.
- Inherited from Pro: canvas #282828, accent and primary #378ef0 (`theme.rs:278-317`).
- Pro (dark) already has dialog-like greys: card/chrome #323232, field #242424, dock #1e1e1e.
- Contrast:
  - White on today's #378ef0 is 3.34:1, below AA.
  - White on #1273e6 is 4.54:1, which passes.
  - #a5a5a5 on #323232 is 5.2:1.
  - #2680eb on a #2f2f2f card is 3.42:1, enough for a non-text outline.
  - The Pro Light Gray and Light themes have contrast tests (`theme.rs:1160-1189`); Pro and Pro Medium have none.

## 3. Photoshop New Document fields versus PhotoCraft

| Photoshop field | PhotoCraft today |
|---|---|
| Name + save-preset icon | Name exists; saving is a text button "Save Preset…" today |
| Width + units | Present (no "Columns" unit) |
| Height | Present |
| Orientation | Present |
| Resolution + units | Present |
| Color Mode + bit depth | Present, except Bitmap and 1-bit: `file.new` accepts only rgb/gray/cmyk/lab at 8/16/32 (`document_preset_cmds.rs:22-39`) |
| Background Contents + swatch | Present, including Custom |
| Recent / Saved / categories | Present |
| Close / Create | Present |
| **Artboards** checkbox | No `file.new` parameter; only `layer.new.artboard` after creation, which adds an undo step and leaves the Background layer |
| **Color Profile** | No `file.new` parameter; only `edit.assignProfile` after creation |
| **Pixel Aspect Ratio** | Not a document property; only the app-wide View > Pixel Aspect Ratio |
| Templates / stock search / "Find more templates" | No equivalent and must not be copied |

## 4. Implementation plan

Everything above keeps working: every field key, `__` key, command and automation path stays.

### A. Dialog palette (colours only, from theme tokens)
1. In `theme.rs`, add `Tokens::new_doc_palette(&self) -> DialogPalette`, a method like `field_selection()` (`theme.rs:807-809`), so the 14 `Tokens` literals and `apply_overrides` stay untouched. Fields: `window`, `well`, `hero`, `card`, `details`, `input`, `dropdown`, `tab_inactive`, `section`, `primary`, `primary_text`, `selected_outline`.
   - Pro and Pro Medium: window #323232, well #252525, hero #2f2f2f, cards #2f2f2f, details #323232, input #252525, dropdown #2f2f2f, inactive tabs #a5a5a5, section labels #a5a5a5, primary #1273e6, outline #2680eb.
   - Every other theme derives the same fields from its own tokens (card, dock, field, accent, primary_bg).
2. Split egui Visuals construction out of `theme::apply` (`theme.rs:974-1020`) into `theme::visuals(&Tokens)`. Add `theme::with_tokens(ctx, t, f)`, which swaps `Id::new("photocraft-theme")` (`theme.rs:750, 979`) for the body and restores it. Widgets read `Tokens::get`, and dropdowns and TextEdits read the ui-scoped `visuals.widgets.inactive.*` and `extreme_bg_color`.
3. In `dialogs.rs:176`, give NewDocument its own frame: `Frame::popup(..).fill(pal.window)`, `inner_margin` around 0, with the body painting the well and details areas.
4. Optional global recolour (part 1 of the request): set Pro and Pro Medium `primary_bg` to #1273e6 and `accent` to #2680eb. White on the button rises from 3.34 to 4.54:1.

### B. Shell
- `dialogs.rs:198-207`: width becomes `min(1040, screen width − 48)` with a minimum of 760.
- Keep the title drag band.
- Keep `dialog_buttons` (Close outlined pill, Create blue pill). See the open question about button order.

### C. Layout (`new_doc_ui::body`)
1. **Tabs** in the order Recent, Saved, Photo, Print, Art & Illustration, Web, Mobile, Film & Video (change :504). Keep the exact labels and the pointing-hand cursor; active tab in text colour with a 2 px underline, inactive in `pal.tab_inactive`; add `widget_info(SelectableLabel, selected)`.
2. **Left well** (`pal.well`, radius_lg):
   - A hero card (`pal.hero`), on the Recent tab only: a painted illustration plus our own wording, "Start a new canvas" and "Choose a preset below, or set your own size in Preset Details." No Adobe wording, templates or search.
   - The heading: Recent → "YOUR RECENT ITEMS ({n})"; Saved → "YOUR SAVED PRESETS ({n})"; other tabs keep "BLANK DOCUMENT PRESETS ({n})".
   - The grid: columns fit the available width; keep 164 px cards with an 8 px gap so the test click offsets still hold; scroll max ~3 rows.
3. **Cards**:
   - Fill `pal.card`. Selected: same fill plus a 2 px `pal.selected_outline` stroke at radius_lg (replacing the `row_selected` fill at :557-570).
   - A painted category glyph, aspect-correct, in a 40 px box.
   - Title via `card_title`; size line unchanged as "W x H unit @ N ppi".
   - Add `resp.widget_info(WidgetInfo::selected(Button, true, on, title))`.
4. **Saved tab**:
   - Show saved presets as the same cards, labelled with the preset name, tooltip "W × H px @ ppi · MODE/depth".
   - An always-visible small trash icon button labelled "Delete" with tooltip "Delete Preset", plus a context-menu Delete. Keep `apply_saved_preset`, double-click create and "No saved presets yet."
5. **Details panel** (`pal.details`, 300 px):
   - "PRESET DETAILS".
   - Name TextEdit plus a painted save-preset icon button whose accessible label stays "Save Preset…"; it toggles the existing `__savingPreset` form directly below.
   - Width/Height/Resolution keep their SpinButton order. Link the captions with `labelled_by`.
   - The Height row: "Orientation" label immediately followed by the two 24 px buttons (test geometry), then the new **Artboards** checkbox (`widgets::checkbox`), stored as `artboards: bool`.
   - Color Mode + depth, Background + swatch as today.
6. **Advanced Options**: collapsible, closed by default, open state in field `__advanced` (styled like `props_layout::section`, `props_layout.rs:66-95`, but kept in dialog fields so agents can drive it).
   - Color Profile dropdown: "Working space ({profile})" (the default, untagged), the built-ins whose colour space matches the mode (`edit.profileInfo`), and "No color profile (untagged)". Stored as `profile`.
   - Pixel Aspect Ratio dropdown: the 8 `view.pixelAspectRatio.*` ids with their menu labels via `tr_id` (`menu_catalog.rs:637-644`). Stored as `__pixelAspect`.
   - No new SpinButtons and no extra TextInput while closed, so the `field_tab` test stays valid.

### D. Engine additions (Everything is a command)
1. Extend `file.new`'s params doc and `validate_new_params` with:
   - `"artboards":bool=false`: create the document as an artboard group "Artboard 1" at canvas size, whose Artboard.background comes from the background choice, containing a transparent "Layer 1" and no Background layer. Reuse the `artboard_cmds.rs` helpers.
   - `"profile":"working|<builtin id>|none"="working"`: resolve as `assign_profile` does (`color_cmds.rs:908-930`), rejecting a colour space that does not match the mode, and set `doc.icc_profile` before `add_document`, so no history step.
2. `DocumentSettings` gets `#[serde(default)] artboards` and `profile` (and `pixel_aspect` as display-only, like `unit`). `command_params` emits them only when they differ from the default, so old presets, Recent entries and their duplicate check are unchanged.
3. Add the new keys to `NEW_DOCUMENT_REMEMBERED` and a bool branch to `remembered_new_document_value` (`lib.rs:2353-2362`). Update `holds()`.
4. Pixel aspect: on Create, if `__pixelAspect` is not "square", run the existing UI command `view.pixelAspectRatio.<id>` (`view_cmds.rs:709-711`). Document that it is app-wide. A per-document field would need `doc` + `format` manifest + PSD changes (AGENTS.md:136-141).

### E. Home screen (colours only)
In `start_screen`, paint a background fill, a card surface behind the column, and the primary button in the palette (home background #1e1e1e, cards #2c2c2c, button #1372e6), all as `Tokens` methods. No layout change.

### F. Documentation
Update docs/ui-design.md (a New Document section), docs/control-protocol.md:61 and :115-119 (new fields), scorecard/ui.toml:86-90, the devlog, and an ATTRIBUTION note for the palette values (original values chosen by observation).

### New `tl!` strings (all 20 catalogs)
- "YOUR RECENT ITEMS ({n})"
- "YOUR SAVED PRESETS ({n})"
- "Start a new canvas"
- "Choose a preset below, or set your own size in Preset Details."
- "Advanced Options"
- "Working space ({profile})"
- "No color profile (untagged)"
- "Delete Preset"
- Optional: "Double-click a card to create it right away."

Reused: Artboards, Color Profile, Pixel Aspect Ratio, Save Preset…, the pixel-aspect menu labels.

### Icons drawn in code (original, painter-drawn, aspect-aware)
- Photo: a frame with a mountain and sun.
- Print: a page with a folded corner.
- Art & Illustration: a page with a diagonal brush stroke.
- Web: a browser window with a bar and three dots.
- Mobile: a rounded phone with a speaker slot.
- Film & Video: a frame with sprocket holes.
- Clipboard: a clipboard with a clip.
- Recent / Custom: a plain page.
- Saved: a page with a bookmark ribbon.
- Save preset: a page with a down arrow into a tray.
- Hero: three overlapping pages with a "+" badge.

Existing Lucide icons reused (already attributed, ATTRIBUTION.md:29): rectangle-vertical, rectangle-horizontal, chevron-down/right, trash.

### Tests to update
- `new_doc_ui.rs:1405-1406` and `:1423`: the heading on Recent becomes "YOUR RECENT ITEMS".
- `:882-894`: the card-width parameter, if the card width changes.
- `:1113-1137` and `:1317`: Saved presets are now cards; the "Delete" label is kept.
- `:1526`: the tab list (order).
- `field_tab.rs:184-215`: must still pass unchanged.

### Tests to add
- **UI**
  - Saved is the second tab; tabs and cards expose their selected state.
  - The hero appears only on Recent; the correct heading appears per tab.
  - Selected card outline; Advanced Options toggles via `ui.dialog.set __advanced`.
  - Profile and pixel-aspect fields reach `file.new` / the view command.
  - Artboards checkbox → `file.new {"artboards":true}`.
- **Engine**
  - `file.new` with artboards creates one artboard and no Background, and honours each background choice.
  - The profile is set and its description checked; a CMYK document with sRGB is an Err; "none" leaves it untagged.
  - Bad types are an Err (and run `panic_hunt`).
  - `DocumentSettings` round-trips, and old JSON without the new fields still loads.
  - Remember-tests cover the new keys.
- **Theme**: contrast for the palette in Pro and Pro Medium — text ≥ 4.5:1 on window/well/hero/details/input, white on primary ≥ 4.5:1, outline against card ≥ 3:1.
- **Visual check**: the `snapshot` example with `--script '[["ui.dialog.open",{"kind":"newDocument"}]]'` at 1440x900, 1280x720 and 800x480, in every theme.

## 5. Notes for the colours-only recolour (Pro Medium, `theme.rs:208-227`)

| Item | Token | Today | Target |
|---|---|---|---|
| Top bar | chrome | #535353 | already matches |
| Canvas surround | canvas | #282828 | already matches |
| Selected layer row | row_selected | #6b6b6b | already matches |
| Dim text | text_faint | #a0a0a0 | already matches |
| Panels | card (:212) | #535353 | #4d4d4d; still between Pro and Light Gray, as the ordering test needs (`theme.rs:1184-1185`) |
| Panel tab row and document tab strip | tab_strip (:224; also `canvas.rs:2407`) | #4a4a4a | #424242 |
| Rulers | chrome (`rulers.rs:335`) | #535353 | #474747, needs its own token or method |
| Status bar | chrome (`panels.rs:1606`) | #535353 | #4b4b4b, needs its own token or method |
| Body text | text | #eeeeee | #e0e0e0 |
| Inputs | field | #454545 | user asked ~#737373, but #eeeeee on #737373 is only 4.09:1, below AA |

## Key locations
- /tmp/claude-0/-home-user/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/photocraft/crates/ui-egui/src/new_doc_ui.rs:497 body(): tabs (502-517), card grid (534-604), PRESET DETAILS column (607-762); the main redesign target
- /tmp/claude-0/-home-user/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/photocraft/crates/ui-egui/src/new_doc_ui.rs:19 CATEGORIES built-in presets; DEPTH_OPTIONS :81; UNITS :84
- /tmp/claude-0/-home-user/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/photocraft/crates/ui-egui/src/new_doc_ui.rs:400 recent_cards (Clipboard + recent + uncovered defaults); saved_presets :411; save_preset form :452
- /tmp/claude-0/-home-user/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/photocraft/crates/ui-egui/src/new_doc_ui.rs:1010 egui_kittest dialog tests; geometry-dependent clicks at 1405-1424 and 1477-1493
- /tmp/claude-0/-home-user/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/photocraft/crates/ui-egui/src/dialogs.rs:198 NewDocument fixed 800 px width; frame override precedent at :176; Create/Close labels :364-382
- /tmp/claude-0/-home-user/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/photocraft/crates/ui-egui/src/dialogs.rs:558 confirm: runs file.new, remember_new_document, document.recent.add
- /tmp/claude-0/-home-user/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/photocraft/crates/engine/src/commands.rs:401 file.new spec and run (no artboards/profile/pixel-aspect params)
- /tmp/claude-0/-home-user/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/photocraft/crates/engine/src/document_preset_cmds.rs:57 validate_new_params rejects unknown keys (:83); DocumentSettings :97; preset/recent specs :274-337
- /tmp/claude-0/-home-user/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/photocraft/crates/ui-egui/src/lib.rs:2353 NEW_DOCUMENT_REMEMBERED + validator; new_document_fields at :2422
- /tmp/claude-0/-home-user/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/photocraft/crates/ui-egui/src/state.rs:1391 UiState::new_document_fields defaults; Dialog/DialogKind at 443-459
- /tmp/claude-0/-home-user/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/photocraft/crates/ui-egui/src/theme.rs:208 ProMedium tokens; Pro tokens at :278; apply() visuals mapping :974-1020; Tokens::get :749
- /tmp/claude-0/-home-user/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/photocraft/crates/ui-egui/src/widgets.rs:1157 dialog_buttons (platform order); Pro pill buttons at 1213-1232; button label font medium(13) at 1189
- /tmp/claude-0/-home-user/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/photocraft/crates/ui-egui/src/canvas.rs:2627 Home/start screen (start_screen, home_recent)
- /tmp/claude-0/-home-user/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/photocraft/crates/ui-egui/src/control.rs:780 ui.dialog.open newDocument / ui.dialog.set / confirm automation paths
- /tmp/claude-0/-home-user/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/photocraft/crates/ui-egui/src/i18n/mod.rs:1114 every_tl_literal_is_translated test; 20 complete catalogs listed at 191-222
- /tmp/claude-0/-home-user/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/photocraft/crates/ui-egui/src/field_tab.rs:184 Tab-order test: single TextInput, Width/Height/Resolution SpinButton order
- /tmp/claude-0/-home-user/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/photocraft/crates/engine/src/artboard_cmds.rs:229 new_artboard helper logic to reuse for file.new artboards
- /tmp/claude-0/-home-user/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/photocraft/crates/engine/src/color_cmds.rs:908 assign_profile resolve/colour-space check to reuse for file.new profile
- /tmp/claude-0/-home-user/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/photocraft/crates/ui-egui/src/view_cmds.rs:157 PIXEL_ASPECTS (global view option, not per document)
- /tmp/claude-0/-home-user/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/photocraft/AGENTS.md:64 Clean-room, assets and attribution rule; tokens rule at :66; visual verification at :67
- /tmp/claude-0/-home-user/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/photocraft/docs/ui-design.md:30 Tokens/widgets/elision/icon rules (30-50, 91); localisation rules (184-226)
- /tmp/claude-0/-home-user/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/photocraft/ATTRIBUTION.md:29 Lucide icon row; palette-precedent rows at 55-57

## Open questions
- Dialog button order: widgets::dialog_buttons puts Create before Close on Windows/Linux (widgets.rs:1124-1131) and every modal shares it. Photoshop's dialog shows Close then Create on the right. Override it only for New Document, or keep the platform order?
- Should Pro and Pro Medium primary_bg and accent change globally to #1273e6 and #2680eb (affects every dialog's OK button and focus rings), or only inside the New Document palette?
- Should the Artboards and Color Profile capabilities be added to file.new in the engine (recommended by 'everything is a command'), or is a UI-only change preferred (running layer.new.artboard / edit.assignProfile after creation, which adds history steps and leaves the Background layer)?
- Pixel Aspect Ratio is app-wide view state, not per document. Is it acceptable for the dialog to set the global view option, or should a per-document field be added (doc + format manifest + PSD mapping)?
- The user's input colour (#737373) gives only 4.09:1 contrast with #eeeeee text. Keep Pro Medium field #454545, or accept the lower contrast?
- Should the hero card appear only on the Recent tab (saves vertical space at small window sizes), or on every tab?
- The ../craftrules standards referenced by AGENTS.md are not in this clone; they may hold more cross-app UI or colour rules (e.g. shared VectorCraft palette conventions) worth checking with a maintainer.