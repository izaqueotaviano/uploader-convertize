## VectorCraft: create-new-document flow map and Photoshop-style redesign plan

Citations are relative to the read-only clone `/tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft` (commit 0d0ea35, 2026-10-13).

**Use the newer checkout for the work.** `/home/user/vectorcraft` is at 0a33cff "Release 0.11.0".
- These files are byte-identical in both checkouts: `dialogs/new_document.rs`, `engine/cmd/newdoc.rs`, `dialogs/modal.rs`, `dialogs/form.rs`, `icons.rs`, `tests_home.rs`.
- Line numbers are shifted in 0.11.0 for:
  - `canvas.rs`: `home()` 2024, `recent()` 2066
  - `widgets.rs`: `tab_bar` 1758, `orientation_button` 1787, `combo` 699
  - `menus.rs`: `file.newDialog` dispatch 971, `home_showing` 3035
  - `dialogs/mod.rs`: registry rows 215 and 259
- 0.11.0 adds a theme test, `slider_rails_show_on_every_panel` (`theme.rs:357-363` there). It requires `|button_border.r - panel.r| >= 24` in every brightness, which constrains the recolour.

### 1. Rules that constrain UI, colour, icon and asset work (quoted)

**Clean-room**
- CLAUDE.md:16: "Never launch, run, script, automate (COM, AppleScript, ExtendScript, UI automation), screenshot or measure Illustrator or any other Adobe application, and never compare our output against one."
  - This conflicts with using a palette measured from Photoshop screenshots.
  - There is a precedent in the code: `theme.rs:146` says "Measured from Illustrator 2026 (plan/illustrator/10-observed-ui.md §1)".
- CLAUDE.md:19: "Behaviour comes only from public documentation ... and from files users send us that they own (used locally, never committed). Never copy Adobe icons, artwork, presets or wording beyond feature names."
  - So we must not use "Let's start something new.", "YOUR RECENT ITEMS", Firefly, Stock, or the "Photo" preset set.

**Assets**
- CLAUDE.md:22-23: "Assets: no Adobe iconography or images — ever ... Never add, copy, trace, redraw-from, embed or ship any icon, image, artwork, cursor ..."
- CLAUDE.md:29-30: every asset file needs a row in ASSETS.md, and `cargo xtask assets` fails otherwise. The checker is `xtask/src/assets.rs:1-40` (svg, png and similar, plus everything under `assets/`).
- CLAUDE.md:33 and ASSETS.md:7: "Prefer art generated in code for defaults" / "Generated-in-code art is original and has no file to list."
- CLAUDE.md:34 and ASSETS.md:5: reference screenshots are never committed.

**Code rules**
- No panics: CLAUDE.md:35-38 (no `unwrap`/`expect`/`panic`/indexing on data outside tests).
- CLAUDE.md:43: "Everything is a command ... UI-only commands live in `crates/ui-egui/src/menus.rs` (`UI_COMMANDS`)."
- CLAUDE.md:45: "The UI is thin ... Colours come from `theme::Tokens`." `theme.rs:40`: "Never hard-code a colour in a widget."
- CLAUDE.md:46: Rust only, never break wasm.
- CLAUDE.md:48: `cargo xtask ci`, one task id per commit.
- CLAUDE.md:53: "For UI work, look at the result (take `ui.screenshot`) ... cover panels with a headless egui frame test."
- CLAUDE.md:66: update the parity, gaps and ROADMAP docs in the same PR.

**Vendor names in strings**
- `xtask/src/brands.rs:1-33`: string literals in non-test Rust may not contain adobe, illustrator, photoshop and similar names; text says "the reference app". Comments are exempt (`brands.rs:6`).

**Translations**
- Every `tl!("literal")` must exist in all 14 catalogs that claim complete menus (`i18n/tests.rs:395-404`). Those are ja, ko, vi, cs, de, es, fr, it, ru, uk, hu, pl, zh-hant, zh-hans (`i18n/mod.rs:101-203`). pt-br is partial (`mod.rs:179-183`).
- Translations are written clean-room from the meaning of the English (`zh-hant.tsv:12-15`).

**Missing or stale rule files**
- There is no `ui-guidelines.md` or ATTRIBUTION file in the repo.
- `icon_data.rs:2` points to `crates/ui-egui/README.md`, which does not exist.
- CLAUDE.md:20 mentions `cargo xtask cleanroom`, but `xtask/src/main.rs:43-56` has no such command. CI runs fmt, clippy, test, assets, brands, layers and wasm (`main.rs:195-206`).

### 2. Current flow

**Entry points**
- `file.newDialog` (Cmd+N) is a UI command (`menus.rs:168`). It dispatches at `menus.rs:953-956` to `dialogs::open_new_document` (re-exported at `dialogs/mod.rs:112`).
- The File menu has "New…" and "New from Template…" (`menus.rs:2061-2062`). Template opening is at `menus.rs:975`.
- Home screen:
  - `app.home` is at `menus.rs:169, 957-960`. Whether Home shows is decided by `home_showing` (`menus.rs:3009-3011`) from `ui.home` (`state.rs:411`) and `prefs.show_home_screen` (`engine/lib.rs:626`).
  - `canvas::show` draws Home first (`canvas.rs:157-162`). `home()` is at `canvas.rs:1948-1987`:
    - background `t.panel_darker` (1951)
    - title and subtitle (1955-1957)
    - New file / Open pills (1959-1967)
    - Recent Files list (1991-2015)
    - six hard-coded quick-start presets drawn with `dialogs::preset_card`; a click runs `file.new {preset}` (1973-1981)
    - Community links (1984-1986)
- Control channel:
  - `engine.execute {command}` goes through `app.run`, so it reaches UI commands too (`control.rs:142-150`).
  - `ui.dialog.set {field, value}` is at `control.rs:296-303`; `ui.dialog.confirm` and `ui.dialog.cancel` follow at 304-308.
  - `ui.screenshot` is at `control.rs:319`.

**Dialog: `crates/ui-egui/src/dialogs/new_document.rs`**

Registration and state:
- Registered at `dialogs/mod.rs:213` (`NewDocument`) and `:257` (`NewDocumentMore`).
- The kinds are `KIND="newDocument"` (:22) and `MORE="newDocumentMore"` (:24). Both specs are `DialogSpec::window` (:26-27).
  - So `dialogs::show` returns early into the dialog's own window (`mod.rs:397-399`).
  - The shared-frame first-field autofocus (`mod.rs:421-422`, `widgets.rs:290-297`) and the shared Enter handling (`mod.rs:450`) do not apply.
- State is the generic `Dialog {kind, fields}` (`state.rs:214-240`).
- Field keys are a contract with `ui.dialog.set` and the tests.
  - `PARAMS` (:30-43): `preset`, `name`, `width`/`height` (pt), `units`, `artboards`, `artboardLayout{layout, columns, spacing, rightToLeft}`, `bleed[t,b,l,r]`, `backgroundContents`, `colorMode`, `rasterEffectsPpi`, `previewMode`.
  - Also `category`, `advanced`, `bleedLinked`, `presetName`, and the private `__applied` (:45) and `__saving` (:47).

Logic:
- `open` (:70-76): starts on Recent (or Print when Recent is empty), applies that category's first preset, and sets the name with `peek_untitled`.
- `apply` (:79-92) fills the fields from a preset. `sync` (:96-115) re-applies a newly chosen preset, and any edit afterwards blanks `preset` (the settings become custom).
- `confirm` (:118-129) runs `app.run("file.new", PARAMS)`. It drops unknown preset names such as Recent's "Custom". The dialog closes only on success; otherwise it stays open and shows the error (`Buttons::finish` :168-176).

Layout of `show` (:179-206):
- Modal window via `window()` (:155-157) → `modal::show(ctx, id, Id("dialog", id), -20, margin 0)`.
- Drag band down to top + 44 (:187).
- Left column: margins 22/14/14/18, width 640, height `HEIGHT`=600 → `presets()`.
- Right column: fill `t.panel_darker`, margin 18, width `DETAILS`=292 → `details()`.

Left column, `presets()` (:210-249):
- `widgets::tab_bar` over `newdoc::category_names()` (:212-216).
- Heading "RECENT", "SAVED" or "BLANK DOCUMENT PRESETS" followed by (n) (:219-226). Empty-state hints at :228-232.
- A scroll area of wrapped cards (:234-247).
  - Selected = applied with the same name and size (:239).
  - A click applies the preset; a double-click also creates the document (:241-244).

The card, `preset_card` (:264-292), is public and shared with Home:
- Size 146×150.
- Fill `t.panel_darker`, or `t.hover` when hovered or selected.
- Selected adds a 2 px `t.accent` outline, radius 6 (:269-272).
- A white page thumbnail in the preset's proportions with a black shadow (:273-279).
- Name in semibold 11.5, up to 2 rows (:281-289), then the size label (:290).

Right column, `details()` (:295-359):
- "PRESET DETAILS" label.
- Name field plus a "save" icon button that toggles the Save Preset row, defaulting the name to "Preset {number}" (:301-312).
  - The Save Preset row (`save_row`, :362-385) runs `file.newPresets.save`, then switches to Saved and selects the new preset.
- Width + Units dropdown with all 10 units (:318-322; `UNITS` :49-60; `units_dropdown` :387-392).
- Height / Orientation / Artboards row:
  - Orientation toggles swap width and height (:395-407).
  - Artboards is a spinner, 1–1000 (:409-416).
- Bleed: `form::bleed`, four fields plus a link toggle, 0–72 pt (`form.rs:603-639`).
- Background Contents dropdown plus a swatch chip (:419-434; options at :61).
- Advanced Options toggle (:450-469) holding Color Mode (:62), Raster Effects (`RASTER_PPI`, `newdoc.rs:156`) and Preview Mode.
- More Settings button (:349-351).
- Close and Create at the bottom right (:353-358).

More Settings, `show_more` (:472-585):
- Name and Profile.
- Artboards count plus 4 layout icons and a Right-to-Left toggle (:501-518).
- Spacing and Columns (:519-533), Size (:535-544).
- The same Width / Height / Bleed / Background / Advanced fields.
- "Templates…" runs `file.newFromTemplate` (:566, 577-583).
- Cancel returns to New Document (:571-573). Create Document confirms.

**Engine: `crates/engine/src/cmd/newdoc.rs`** (registered at `cmd/mod.rs:264`)

`file.new`:
- Spec at `cmd/edit.rs:16-24`; the full params doc is at :21.
- Implemented by `file_new` (:554-584). It looks up the preset with `find` (:533-541; saved presets win).
- `with_params` (:201-264) validates:
  - units; width/height as pt or "210 mm"
  - orientation; artboards 1–1000
  - layout (:267-296); bleed; background
  - colorMode rgb|cmyk; rasterEffectsPpi 1–2400; previewMode
  - that everything fits on the canvas
- A changed size renames the settings "Custom" (:560-566).
- Title comes from `name`/`title` or the next untitled name (:569-574).
- Overprint preview runs `view.overprintPreview` (:579-581).
- `remember` (:587-592) keeps 12 Recent entries.
- Returns `{index, previewMode}`.

Presets commands:
- `file.newPresets` query: :14-22, implemented by `list` (:594-608).
- `.save`: :23-31, implemented by `save` (:610-628); names 1–64 characters, same name replaces.
- `.delete`: :32-40, implemented by `delete` (:630-636). **It has no UI anywhere** (no hits in `crates/ui-egui`).

Data:
- `DocSettings` is at :109-130; the default is Letter, 612×792 pt (:132-151).
- `size_label` gives "1920 × 1080 px" (:176-179).
- Built-in presets are generated in code in `CATEGORIES` (:395-499):

| Category | Presets | Colour mode | Raster ppi |
|---|---|---|---|
| Mobile | 13 | RGB | 72 |
| Web | 6 | RGB | 72 |
| Print | 8 | CMYK | 300 |
| Film & Video | 6 | RGB | 72 |
| Art & Illustration | 5 | RGB | 300 |
| Branding | 7 | CMYK | 300 |
| Social | 9 | RGB | 72 |

- Tab order (:502-504): Recent, Saved, then the seven categories above.
- Screen presets stay in px; the others use the units preference (:508-519).

Storage:
- Saved presets live in `prefs.new_doc_presets` and Recent in `prefs.recent_new_docs` (`engine/lib.rs:799-805`). Resetting preferences keeps them.
- The journal records the created date only for replay (`lib.rs:548-549`).

**Keyboard**
- Cmd+N opens the dialog (test at `tests_home.rs:86-92`).
- Enter creates only when no widget has focus (:169).
- Escape closes any dialog (`shortcuts.rs:215-227`) through `dialogs::cancel` (`mod.rs:336-342`).
- Double-click on a card creates. Enter in Preset Name saves (:366-367).
- Missing: autofocus, arrow-key navigation between cards, and a visible focus ring.

**Translations**
- Dialog strings are already in all 14 complete catalogs. I checked: RECENT, SAVED, BLANK DOCUMENT PRESETS, PRESET DETAILS, Save Preset, Width, Height, Units, Orientation, Artboards, Bleed, Color Mode, Raster Effects, Preview Mode, Background Contents, More Settings, New from Template…, Templates…, Create, Close, Delete Preset.
- Gaps found:
  - Tab category names are passed as data and translated with `tl!(tab)` (`widgets.rs:1745`), so the coverage test cannot see them. As a result:
    - "Mobile", "Branding", "Social", "Film & Video" and "Art & Illustration" are in only 6 of 14 catalogs; "Web" in 2 of 14.
    - None of them are in pt-br.
  - `ja.tsv:3162` has a stale "Preset {}" while the code uses "Preset {number}" (:307-308).
  - The window's accessible name is the raw kind "newDocument" (:156 passes `id` as the title; see `modal.rs:10-13`). "New Document" is in no catalog.

**Accessibility**
- AccessKit is on by default (`apps/vectorcraft/Cargo.toml:13,15`).
- These custom-painted widgets expose no `WidgetInfo`, so screen readers get unlabelled buttons with no role or selected state:
  - `primary_button` / `secondary_button` (`widgets.rs:91-114`)
  - `flat_button` (35-48)
  - `icon_button`, tooltip only (11-32)
  - `tab_bar` (1738-1763)
  - `orientation_button` (1767-1784)
  - `preset_card`
- Only `section_toggle_name` sets it (`widgets.rs:141`).

**Theme today**
- `Tokens` is at `theme.rs:41-96`.
- Dark base (101-143): panel #323232, panel_darker #282828, input #1f1f1f, accent #378ef0, accent_strong #1473e6, pasteboard #1e1e1e.
- MediumDark is the default brightness (:11); its overrides are at 147-170: panel and app_bar #535353, panel_darker and tab_strip #424242, input #454545, pasteboard #606060.
- Tokens are global context data (`theme.rs:224-226, 297`).
- Where the dialog takes its colours:
  - modal frame fill = `t.panel` (`modal.rs:32`)
  - dropdowns = `t.input` (`widgets.rs:690-691`)
  - text fields = `t.input` / `t.input_border` (`form.rs:122-126`)

**Tests that cover it**
- UI, in `new_document.rs`:
  - `only_built_in_preset_names_are_translated` (:596)
  - `a_double_clicked_preset_creates_the_document` (:622-663; finds the card by the text "Phone 393", 50 ms frames, 1400×1000 screen)
  - `a_preset_fills_the_details_and_create_makes_the_document` (:666-694)
  - `every_category_and_more_settings_draw_and_save_preset_saves` (:697-724)
- UI, elsewhere:
  - `dialogs/tests.rs:37-58` (kinds) and `:61-112` (`every_dialog_draws`)
  - `dialogs/tests.rs:129-156` (New Document confirm)
  - `dialogs/tests_modal.rs:85-117`: drags at window top-left + (40,10); window id ("dialog","newDocument"). It must keep passing.
  - `panels/tests_units.rs:108-118` (Letter shown in mm)
  - `tests_home.rs:24-135`
- Engine: `tests_newdoc.rs` (13 tests), `tests_params.rs:54-64`.
- How they run headlessly: `egui::Context::default` + `theme::install_fonts` + `theme::apply` + `ctx.run_ui(raw, |ui| dialogs::show(app, ui.ctx()))` (:602-610). They collect `Shape::Text` positions (:643-651) and inject PointerMoved and PointerButton events.
- Visual precedent: `chrome.rs:1117-1148` renders PNG fixtures with `egui_kittest` + wgpu when `CRAFT_UI_VISUAL_FIXTURES` is set. `egui_kittest` is a dev-dependency (`crates/ui-egui/Cargo.toml:37`).

### 3. Implementation plan (nothing lost)

Keep unchanged: the kinds, the window id, every field key, and every command (`file.new`, `file.newPresets*`, `file.newFromTemplate`). No engine change is needed.

**A. Tokens (`theme.rs`)**
- Add tokens:

| Token | Dark / MediumDark |
|---|---|
| `sheet` | #323232 |
| `sheet_well` | #252525 |
| `sheet_card` | #2f2f2f |
| `sheet_card_hover` | ~#383838 |
| `sheet_input` | #252525 |
| `sheet_dropdown` | #2f2f2f |
| `tab_idle` | #a5a5a5 |
| `card_selected` | #2680eb |
| `home_bg` | #1e1e1e |
| `home_card` | #2c2c2c |

- MediumLight and Light map these to their existing light values, so light themes stay light.
- Set `accent_strong` to #1273e6; coordinate this with the recolour task.
- Add `Tokens::sheet(self)`: a copy with panel=sheet, panel_darker=well, input=sheet_input, button=sheet_dropdown, text_dim=tab_idle, hover=card_hover.
- Add `theme::with_tokens(ctx, t, f)`: swaps the Tokens for the duration of `f` and always restores them.
- Wrap `show` and `show_more` in it. Also set `ui.visuals_mut()` (`extreme_bg_color`, `inactive.bg_fill`) inside the window. Then `form.rs` and `widgets.rs` pick up the dark dialog colours without per-widget edits.
- Code comments should say "reference palette supplied by the user", and no vendor name may appear in string literals.

**B. Window**
- Left column fill `sheet_well`, with radius 6 on its left corners. Right column fill `sheet` (it is `panel_darker` today, at :196).
- Pass `tl!("New Document")` as the title. `modal.rs:26` sets the id explicitly, so the tests are unaffected.
- Keep `drag_band` and a top margin of at least 14.

**C. Left column**
1. Tabs: active tab white text with a 2 px white underline; idle tabs `tab_idle`.
   - Add a styled variant of `tab_bar` rather than changing the shared one. It is also used at `document_setup.rs:47`, `export_for_screens.rs:259`, `revolve.rs:68,143` and `save_for_web.rs:348`.
   - Put the row in a horizontal scroll area so long translations do not clip.
   - Make the category labels `tl!()` literals through a `category_label()` function.
2. Hero card: full width × ~112, fill `sheet_card`, radius 8.
   - Our own heading and body text.
   - A "New from Template…" link that runs `file.newFromTemplate`. Factor this out of :577-583.
   - A code-drawn illustration on the right.
   - Shrink the grid's scroll area to about 370 px so two rows of cards still show.
3. Section heading: keep the existing RECENT (n) / SAVED (n) / BLANK DOCUMENT PRESETS (n). This needs no new strings and does not copy the reference wording.
4. New dialog card, `preset_tile`, about 146×132. Leave Home's `preset_card` as it is, with colours only.
   - Fill `sheet_card`, hover `sheet_card_hover`, selected 2 px `card_selected` outline at radius 6, and a focus ring.
   - Category outline glyph, 1.5 px `t.icon`.
   - Name, then one dim line "{size_label} · RGB|CMYK".
   - `WidgetInfo::selected` with "{name}, {size}".
   - Click and double-click behave exactly as now.
5. Optional additions:
   - A trash icon on Saved cards when hovered, running `file.newPresets.delete`. It uses the existing `trash-2` icon and the existing "Delete Preset" string.
   - Arrow keys move between cards when no field has focus.

**D. Right column, in the reference order, with the same keys**
1. PRESET DETAILS
2. Name + save icon (existing `save` icon), and `save_row` as it is
3. Width + Units (`sheet_dropdown`)
4. Height + Orientation; the selected toggle is filled with `card_selected`
5. Artboards spinner, kept at 1–1000
6. Bleed
7. Color Mode (optionally moved out of Advanced)
8. Raster Effects, in the slot where the reference shows Resolution
9. Background Contents + chip
10. Advanced Options: Preview Mode
11. More Settings
12. Close (outlined light-grey pill) and Create (blue #1273e6 pill, white semibold) at the bottom right

**E. Accessibility**
- Add `widget_info` to `primary_button`, `secondary_button`, `flat_button`, `icon_button` and `orientation_button`.
- Give tabs the selected state.
- These are shared widgets: the result looks the same and helps the whole app.

**F. Home (colours only)**
- Background `home_bg` (`canvas.rs:1951`).
- Quick-start cards `home_card`.
- The New file pill is already `primary_button`.

**G. Docs**
- `target-app-parity.md:185`, `ui-parity.md`, `localization-parity.md`, and the ROADMAP log.

### 4. New strings (14 complete catalogs + pt-br, clean-room)
- "New Document" (accessible window name)
- Hero heading, e.g. "Start a new document"
- Hero body, e.g. "Pick a preset below, or set your own size in Preset Details."
- Category names made into literals: Mobile, Web, Film & Video, Art & Illustration, Branding, Social. Fill the missing rows; Print, Recent and Saved are already done.
- Fix `ja.tsv:3162` to "Preset {number}".
- Everything else is reused. RGB and CMYK stay untranslated.

### 5. Icons to draw in code
All drawn with the painter in theme colours, with no files, so no ASSETS.md rows are needed (ASSETS.md:7).

| Glyph | Used for |
|---|---|
| Page with folded corner (reuse the fold from `widgets.rs:1776-1781`) | Print, and non-pixel Recent / Saved / Custom entries |
| Phone (speaker slot) / tablet (home dot) / watch (strap stubs) | Mobile |
| Browser window (title bar + 3 dots) | Web |
| 16:9 frame with sprocket ticks and a play triangle | Film & Video |
| Frame with a cubic Bézier, two square anchors and a handle | Art & Illustration |
| Business card with a circle mark and text lines | Branding |
| Square post with a speech-bubble tail | Social |
| Two offset artboards with an accent Bézier and handles | Hero illustration |

- Choose the glyph with `category_of()`: a built-in name maps to its category (like `is_builtin_preset`, :253-255); otherwise px means a screen glyph and anything else a page glyph.
- Reuse the icons already in the repo, which have ISC rows: save, chevrons, link/link-2-off, trash-2.
- Never trace the reference app's glyphs.

### 6. Tests

**Keep green**
- `new_document.rs` :622, :666, :697. "Phone 393×852" must stay visible at 1400×1000 below the hero.
- `tests_modal.rs:85-117`.
- `tests_units.rs:108-118`.
- `dialogs/tests.rs`.
- `tests_home.rs`.
- Engine `tests_newdoc.rs`, unchanged.

**Add**
1. Cards show their name and "390 × 844 px · RGB"; a Print card shows CMYK.
2. Exactly one 2 px `card_selected` outline, around the selected card.
3. The sheet palette has the expected hex values, and contrast holds:
   - white on #1273e6 ≥ 4.5:1 (about 4.55)
   - `tab_idle` on #323232 ≥ 4.5:1 (about 5.2)
   - outline vs card ≥ 3:1 (about 3.4)
4. `Tokens::get(ctx)` is restored after the dialog draws.
5. Accessibility through `egui_kittest` queries (no GPU needed): find "Create", "Close", the "Mobile" tab as selected, the window name and the card labels; clicking "Create" makes a document.
6. Keyboard: Enter with nothing focused creates; Escape closes (`shortcuts::handle`); Enter on a focused card only selects it; arrow keys, if added.
7. The hero link runs `file.newFromTemplate`, using the `picks` stub patterns from `tests_picks.rs`.
8. Saved-preset delete, if added.
9. Category label coverage comes automatically through `every_tl_literal_is_translated`.
10. `capture_new_document_visual_fixtures`, gated on `CRAFT_UI_VISUAL_FIXTURES` for every brightness, like `chrome.rs:1117-1148`.

### 7. Reference-layout items with no equivalent

| Reference item | What VectorCraft has | Proposal |
|---|---|---|
| Photo tab | No photo category (vector app) | Omit |
| Resolution + units | No document resolution; nearest is Raster Effects (72/150/300 ppi) | Show "Raster Effects" in that slot, never called Resolution. Cards show RGB/CMYK, not "@ ppi" |
| Bit depth | Colour mode is RGB/CMYK only (`doc/src/lib.rs:338-342`) | Omit |
| Artboards checkbox | Always has artboards, 1–1000 | Keep the spinner |
| Background Black / Background Color / Custom | Only Transparent or White (`doc/src/setup.rs:173-178`) | Keep the two options |
| Color Profile | `file.new` takes no profile; documents use the working spaces (`cmd/colormgmt.rs:28-35`) and can be tagged later (`edit.assignProfile`, :47-53) | Omit, or add an engine param later |
| Pixel Aspect Ratio | None | Omit |
| Stock and template thumbnails, search | None | Original illustration plus "New from Template…" |

Fields only VectorCraft has, which must stay: Bleed, Preview Mode, More Settings (layout, columns, spacing, Right-to-Left), Templates….

**Out of scope here:** PhotoCraft's equivalent dialog is `/home/user/photocraft/crates/ui-egui/src/new_doc_ui.rs`.

## Key locations
- /tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft/CLAUDE.md:16 Clean-room: never screenshot or measure Adobe apps (conflicts with a palette measured from Photoshop screenshots)
- /tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft/CLAUDE.md:22 Asset rule: no Adobe iconography; every asset needs an ASSETS.md row (29-30); prefer art drawn in code (33)
- /tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft/CLAUDE.md:45 Thin UI acting through app.run; colours come from theme::Tokens
- /tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft/ASSETS.md:7 Art generated in code needs no ASSETS.md row
- /tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft/xtask/src/brands.rs:18 Vendor-name check on string literals (adobe, illustrator, photoshop...)
- /tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft/crates/ui-egui/src/dialogs/new_document.rs:30 PARAMS field keys (contract with ui.dialog.set and tests)
- /tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft/crates/ui-egui/src/dialogs/new_document.rs:70 open(): first category (Recent or Print), untitled name
- /tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft/crates/ui-egui/src/dialogs/new_document.rs:118 confirm(): runs file.new with PARAMS
- /tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft/crates/ui-egui/src/dialogs/new_document.rs:155 window(): passes kind id as the accessible title (accessibility bug)
- /tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft/crates/ui-egui/src/dialogs/new_document.rs:179 show(): two-column layout (640 + 292, HEIGHT 600)
- /tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft/crates/ui-egui/src/dialogs/new_document.rs:210 presets(): tabs, heading, card grid, click/double-click
- /tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft/crates/ui-egui/src/dialogs/new_document.rs:264 preset_card(): card drawing, shared with the Home screen
- /tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft/crates/ui-egui/src/dialogs/new_document.rs:295 details(): Preset Details column, Close/Create
- /tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft/crates/ui-egui/src/dialogs/new_document.rs:472 show_more(): More Settings classic form, Templates -> file.newFromTemplate
- /tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft/crates/ui-egui/src/dialogs/new_document.rs:622 Headless double-click test (pattern for new tests)
- /tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft/crates/engine/src/cmd/newdoc.rs:395 CATEGORIES: built-in presets generated in code
- /tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft/crates/engine/src/cmd/newdoc.rs:554 file_new implementation; Recent via remember() at 587
- /tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft/crates/engine/src/cmd/newdoc.rs:14 file.newPresets / .save / .delete specs (delete has no UI)
- /tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft/crates/engine/src/cmd/edit.rs:16 file.new command spec and params doc
- /tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft/crates/engine/src/lib.rs:802 prefs.new_doc_presets (Saved) and recent_new_docs (Recent, 805)
- /tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft/crates/ui-egui/src/menus.rs:168 UI_COMMANDS file.newDialog (Cmd+N) and app.home; dispatch at 953
- /tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft/crates/ui-egui/src/canvas.rs:1948 Home screen home() (colours-only target); recent() at 1991
- /tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft/crates/ui-egui/src/dialogs/mod.rs:213 Dialog registry rows NewDocument (213) / NewDocumentMore (257); window early return at 398
- /tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft/crates/ui-egui/src/dialogs/modal.rs:18 Modal frame: fill t.panel (32), drag_band (53)
- /tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft/crates/ui-egui/src/theme.rs:41 Tokens struct; Dark base 101, MediumDark 147, global storage 224/297
- /tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft/crates/ui-egui/src/widgets.rs:91 primary_button / secondary_button pills (no widget_info)
- /tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft/crates/ui-egui/src/widgets.rs:1738 tab_bar (shared by 5 dialogs, accent underline) and orientation_button at 1767
- /tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft/crates/ui-egui/src/shortcuts.rs:215 Escape cancels any open dialog
- /tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft/crates/ui-egui/src/control.rs:296 ui.dialog.set / confirm / cancel control methods for headless driving
- /tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft/crates/ui-egui/src/i18n/tests.rs:395 every_tl_literal_is_translated: new tl! strings need 14 catalogs
- /tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft/crates/ui-egui/src/dialogs/tests_modal.rs:85 New Document drag-band test that must keep passing
- /tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft/crates/ui-egui/src/chrome.rs:1117 egui_kittest visual fixture capture precedent (CRAFT_UI_VISUAL_FIXTURES)
- /home/user/vectorcraft/crates/ui-egui/src/theme.rs:357 Newer 0.11.0 test: button_border vs panel red gap >= 24 in every brightness

## Open questions
- Clean-room conflict: CLAUDE.md:16 forbids measuring Adobe applications, and this palette was measured from the user's Photoshop screenshots. Does the project owner accept these hex values (theme.rs:146 already cites measured Illustrator colours)? Screenshots must stay out of the repo either way.
- Should the Home screen's quick-start cards adopt the new dialog card look (preset_card is shared), or keep their current layout with colours only, per 'melhorias de cores somente'?
- Move Color Mode and Raster Effects out of Advanced Options into the main column to match the reference order, or keep them in Advanced to keep the diff small?
- Should the New Document dialog stay dark (#323232/#252525) under Medium Light and Light brightness, or follow those light themes (planned: follow them)?
- Add the optional extras: a UI for file.newPresets.delete on Saved cards (the command exists but has no UI), and arrow-key navigation between cards?
- The hero card wording must be original (not 'Let's start something new.'). Is 'Start a new document' / 'Pick a preset below, or set your own size in Preset Details.' acceptable? The 14 catalogs then need clean-room translations and native review.
- Color Profile has no file.new parameter. Omit it (planned), or add an engine `colorProfile` param with tests in a separate task?
- Do the work in /home/user/vectorcraft (0.11.0, newer; some line numbers differ) rather than the scratchpad clone, and should PhotoCraft's dialog (crates/ui-egui/src/new_doc_ui.rs) get the same treatment in a separate mapping pass?