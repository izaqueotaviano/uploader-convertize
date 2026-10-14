## 0. Which copy
I mapped the read-only clone you named, called S below: `/tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft` (storytold upstream, commit 0d0ea35, 2026-10-13). All line numbers are from S unless marked W.

There is a second, writable copy at W = `/home/user/vectorcraft` (fork izaqueotaviano/vectorcraft, one commit 0a33cff "Release 0.11.0", 2026-10-14). It is newer and differs from S in 78 ui-egui files:
- `theme.rs` is the same through line 352. W adds one colour test at W theme.rs:354-363 (see section 5).
- `dialogs/new_document.rs` and `dialogs/modal.rs` are byte-identical.
- `chrome.rs`, `canvas.rs`, `widgets.rs` and `prefs_dialog.rs` have shifted lines. W equivalents: chrome app_bar fill W:32, doc_tabs strip W:374, status_bar W:500, fixtures test W:1280; canvas pasteboard W:203, artboard outline W:386, ruler W:1181, home() W:2024-2026; widgets primary_button W:91, secondary W:103, slider W:1013, tab_bar W:1758.
- Edits will presumably land in W.

## 1. Rules that constrain colour, icon and asset work (quoted)
- CLAUDE.md:15-16: "Clean-room: never use Adobe software (absolute rule…) Never launch, run, script, automate…, screenshot or measure Illustrator or any other Adobe application, and never compare our output against one."
- CLAUDE.md:19: "Behaviour comes only from public documentation…, and from files users send us that they own (used locally, never committed). Never copy Adobe icons, artwork, presets or wording beyond feature names."
- CLAUDE.md:22-23: "Assets: no Adobe iconography or images — ever… Never add, copy, trace, redraw-from, embed or ship any icon, image, artwork, cursor, preset, swatch… or screenshot from Adobe products."
- CLAUDE.md:29-30: every asset needs a row in ASSETS.md, and `cargo xtask assets` fails otherwise. ASSETS.md:5 restates this policy and adds "Screenshots of Adobe software are never committed."
- CLAUDE.md:33: "Prefer art generated in code for defaults."
- CLAUDE.md:34: "Reference screenshots of Illustrator stay local under the gitignored `plan/` and are never committed, published or used as assets."
- CLAUDE.md:45: "The UI is thin… Colours come from `theme::Tokens`." theme.rs:40: "All colours and metrics the UI uses. Never hard-code a colour in a widget."
- CLAUDE.md:46: Rust only, never break wasm. CLAUDE.md:48: run `cargo xtask ci` before every commit; one task id per commit.
- CLAUDE.md:53: "For UI work, look at the result (take `ui.screenshot`, read the PNG)."
- CLAUDE.md:66: when a task lands, update `docs/target-app-parity.md`, `gaps.md`, the checklist (here `docs/ui-parity.md`, whose "Look and feel" row is at :30 and section at :193-198), `roadmap.md` and the ROADMAP.
- Vendor-name gate (development.md:224, xtask/src/brands.rs:18-32): `cargo xtask brands` fails on user-visible string literals containing adobe, illustrator, photoshop, acrobat, creative cloud, pantone and similar. Comments and tests are not checked; the escape hatch is a `brand-ok` comment.
- Localisation: any new `tl!` literal (hero-card text, new headings) must be translated in all 14 `complete_menus: true` catalogs (i18n/mod.rs:101-203), or `i18n::tests` fail (development.md:200-203).
- No ui-guidelines.md exists in the repo.
- Tension to flag: theme.rs:146 says "Measured from Illustrator 2026 (plan/illustrator/10-observed-ui.md §1)", which conflicts with CLAUDE.md:16.

## 2. How colours are defined and applied
**Brightness enum.** `theme::Brightness` has four levels: Dark, MediumDark (the default), MediumLight, Light (theme.rs:8-38). There is no dark/light/system choice.

**Token struct.** `theme::Tokens` holds 38 colour fields plus `radius` and `font_size` (theme.rs:41-96). `Tokens::for_brightness` builds them (theme.rs:99-222):
- `base` is the Dark set (theme.rs:101-143).
- MediumDark overrides 21 fields and takes the rest with `..base` (147-170).
- MediumLight (171-195) and Light (196-220) also use `..base`. So accent, accent_strong, selection, guide, error and the other semantic fields are shared by all four levels.

**Storage and lookup.** Tokens live in egui temp data under `Id::NULL`. `Tokens::get` falls back to MediumDark (theme.rs:224-226).

**`theme::apply`** (theme.rs:295-339):
- Starts from `Visuals::dark()` or `Visuals::light()`.
- panel_fill and window_fill = panel (299-300); extreme_bg_color = input, used for text-field backgrounds (301); faint_bg = panel_darker (302); window_stroke = border (303); window and menu corner radius 6 (304-305).
- Selection bg = accent×0.55, selection stroke = accent, hyperlink = accent (306-308); override_text_color = text (309); shadows are black-alpha literals (310-311).
- Widget fills come from `craft_ui::theme::WidgetPalette { noninteractive: panel, inactive: button, hovered: hover, active: tool_active, open: hover }.apply_to(...)` (313-317). WidgetPalette is in the external git crate craft-ui (Cargo.toml:15, rev 5c874d5), which is not available offline.
- Strokes are then overridden locally (318-321): noninteractive = divider, inactive = none, hovered = input_border, active = accent.
- Spacing and fonts are set at 323-338.

**Where apply runs.**
- First frame: lib.rs:996-999.
- On every preference change: prefs_dialog.rs:104-133. This also replaces `pasteboard` with the Canvas Color preference (93-101, 129-133).

**Local style overrides.** Only six sites change visuals outside theme.rs: widgets.rs:996-1002 (slider), image_trace.rs:212-213, revolve.rs:325-326, theme.rs:237.

**Chrome surfaces and the token each uses:**
| Surface | Token | Where |
|---|---|---|
| App bar | app_bar | chrome.rs:32 |
| Control (options) bar | panel | chrome.rs:217-219 |
| Document tab strip | tab_strip | chrome.rs:374 |
| Active document tab | panel | chrome.rs:405 |
| Status bar | panel | chrome.rs:500-504 |
| Hint bar | panel | chrome.rs:823-825 |
| Toolbar | panel | toolbar.rs:107, 555 |
| Toolbar header | tab_strip | toolbar.rs:146, 582 |
| Dock | panel | dock.rs:93, 120 |
| Shared dock | panel | panel_docking.rs:682, 770 |
| Dock tab row | tab_strip | panel_docking.rs:644-652 (craft_ui DockStyle: background, tab_background, accent) |
| Floating panels | tab_strip / panel_darker | floating.rs:747, 830, 874, 881 |
| Pasteboard | pasteboard | lib.rs:1254, canvas.rs:198 |
| Rulers | ruler + ruler_tick (ticks and labels) | canvas.rs:1166-1227 |
| Empty window | panel_darker | canvas.rs:166 |
| Home screen | panel_darker | canvas.rs:1950-1951 |
| Modal dialogs | panel | dialogs/modal.rs:32 |
| Selected rows | row_selected | 17 files, e.g. layers.rs:164, 650 |

**Buttons** (widgets.rs):
- `primary_button` (91-100): pill radius 14, accent_strong fill, accent on hover, WHITE semibold label.
- `secondary_button` (103-114): pill outlined 1.5 px in text_dim.
- `flat_button` and `split_button` (34-87): button_border outline.
- `paint_icon_button` (17-32): tool_active when selected, hover when hovered.
- `tab_bar` (1738-1763): inactive tabs text_dim, active text_strong, 2 px **accent** underline.
- `orientation_button` (1767+): accent when selected.

**Token use counts** (`t.<field>` in ui-egui): text 180, text_dim 153, text_strong 82, accent 71, icon 54, border 52, input_border 50, hover 50, panel 45, text_disabled 32, input 24, row_selected 20, panel_darker 11, tool_active 11, tab_strip 10, button_border 10, pasteboard 9, accent_strong 4, app_bar 1, ruler 1, button 1.

## 3. Hard-coded Color32 literals
I matched `Color32::(from_rgb|from_rgba_*|from_gray|from_*_alpha|WHITE|BLACK|TRANSPARENT|PLACEHOLDER|…)`.
- **Line count:** 206 lines in crates/ui-egui, excluding theme.rs (5); 0 in apps/; 0 in other crates. W has the same 206.
- **Occurrence count:** about 188 shipped and about 34 in tests, across 48 files.

Worst files by matching lines (grep -c):
| File | Lines |
|---|---|
| canvas.rs | 42 |
| widgets.rs | 33 |
| panels/swatches.rs | 10 |
| panels/layers.rs | 9 |
| prefs_dialog.rs | 8 |
| panels/graphic_styles.rs | 7 |
| dialogs/save_for_web.rs | 7 |
| icons.rs | 5 |
| tests_docsetup.rs, transparency.rs, flattener_preview.rs, brushes.rs, community.rs | 4 each |

Most of these are document or art colours that should **not** follow the UI palette: white paper, checkerboards, swatch fills, anchor handles, and WHITE texture tints. Chrome-relevant ones:
- canvas.rs:381: artboard outline `from_gray(0)` (active) / `from_gray(120)`.
- canvas.rs:207-208: page shadow in black alpha.
- prefs_dialog.rs:95-98: Canvas Color greys.
- find_font.rs:151-159, actions.rs:107/133, navigator.rs:214, transparency.rs:121: ad-hoc reds and oranges that should be t.error / t.warning.
- community.rs:11: Discord #5865F2 (keep).
- Shadows: toolbar.rs:557, canvas.rs:2129, free_transform.rs:61.
- new_document.rs:278-279: card page shadow and white page.
- widgets.rs:93/98: primary button label WHITE (matches the target anyway).

## 4. Theme preference
- Preference `uiBrightness` with choices dark | mediumDark | mediumLight | light (engine/src/cmd/prefscmds.rs:261-267). Defaults are `"mediumDark"` and canvasColor `"matchUi"` (engine/src/lib.rs:936-937), and `UiState.brightness` defaults to MediumDark (state.rs:600).
- It can be changed by the command `window.brightness` (menus.rs:325, 1238-1245), by control `ui.set {brightness}` (control.rs:257-260), and by the macOS Appearance menu.
- Canvas Color (prefscmds.rs:268+) overrides `pasteboard` unless it is matchUi.
- There is **no System or follow-OS option.** docs/ui-parity.md:197 lists it as missing ("#825").
- The Photoshop main-window palette lines up with **MediumDark**: app_bar and panel are already #535353, tab_strip and panel_darker already #424242.

## 5. Tests that pin colours
No test pins a UI-chrome hex value, and there are no pixel-snapshot comparisons. The sensitive tests:
- theme.rs:345-352 checks only the `dark` flag.
- **W only, theme.rs:354-363 `slider_rails_show_on_every_panel`:** asserts |button_border.r − panel.r| ≥ 24 for every brightness. With panel #4d4d4d, button_border must be ≥ #656565 or ≤ #353535; #747474 passes.
- prefs_dialog.rs:417-433 compares the pasteboard to the themed token plus the literal greys c8/96/5a and WHITE.
- Checkbox outlines must have a non-zero stroke at every brightness: prefs_dialog.rs:392-411 and properties.rs:592-611.
- artboards.rs:340, 375, 455 find shapes by `fill == row_selected`, so row_selected must stay unique (≠ hover and ≠ other fills).
- Relative token reads: layers.rs:1378, 1399, 1901 (text, divider); align.rs:427 (tool_active); edit_toolbar.rs:741 (text_disabled); canvas.rs:2600 (selection); tests_docsetup.rs:62 (bleed).
- `#rrggbb` strings in tests_* files are document colours, not UI colours.

## 6. Mapping: token → palette (MediumDark arm, theme.rs:147-170)
| Token | Now | Target | Notes |
|---|---|---|---|
| app_bar | #535353 (148) | #535353 | Keep. |
| panel | #535353 (149) | #4d4d4d | Also fills the control bar, toolbar, status bar, hint bar, dialogs, active doc tab and egui window/panel fill. See section 7. |
| tab_strip | #424242 (151) | #424242 | Keep. |
| panel_darker | #424242 (150) | #424242 | Keep for panel strips; move Home and New Document off it. |
| input | #454545 (152) | #737373 as specified | Contrast flag: #e0e0e0 on #737373 is 3.59:1. Confirm. |
| input_border | #5f5f5f | Unspecified; about #858585 if input is #737373 | |
| border | #383838 | Keep (or about #2e2e2e) | |
| divider | #4b4b4b (155) | About #3a3a3a | Must change: invisible on a #4d4d4d panel. |
| text | #d1d1d1 | #e0e0e0 | 6.4:1 on #4d4d4d. |
| text_strong | #ffffff | #ffffff | Keep. |
| text_dim | #b0b0b0 | #a0a0a0 | Contrast flag: 3.23:1 on #4d4d4d, 2.94:1 on #535353. |
| text_disabled | #7a7a7a | Keep | |
| icon | #c2c2c2 | About #d0d0d0 | Unspecified. |
| hover | #606060 | About #5c5c5c | Must stay different from row_selected. |
| tool_active | #303030 | Keep | |
| row_selected | #52677c (bluish) | #6b6b6b | |
| pasteboard | #606060 | #282828 | Only for users on the default canvasColor=matchUi. |
| ruler | #333333 | #474747 | |
| ruler_tick | #8a8a8a | About #b0b0b0 | Also colours the ruler labels; 2.69:1 now, 4.28:1 after. |
| button | #535353 | About #5a5a5a (or same as input) | egui's inactive widget fill, e.g. ComboBox. |
| button_border | #747474 | Keep | The W test needs ≥ 24 from panel. |
| accent | #378ef0 (base:116) | #2680eb | Override in the MediumDark (and Dark) arms, not in base. |
| accent_strong | #1473e6 (base:117) | #1273e6 | Home's #1372e6 is about the same. |

Leave unchanged: selection, anchor_selected, smart_guide, guide, bleed, error, warning, axis_*, highlight, caption_close, measure_bg. These are canvas or semantic colours.

If the user means the `Dark` level instead, add an explicit `Brightness::Dark => Tokens{…, ..base}` arm (theme.rs:145 currently returns `base`). Editing `base` would leak into the light levels.

## 7. What tokens alone cannot do (needs code or new tokens)
1. **Options bar and toolbar #535353 vs panels #4d4d4d vs status bar #4b4b4b:** all use `t.panel` (chrome.rs:219, 504, 825; toolbar.rs:107, 555; dock.rs:93). Needs new fields (e.g. `bar`, `status_bar`) and edits at those sites.
2. **Home screen (#1e1e1e bg, #323232 top bar, #2c2c2c cards):**
   - The bg is `panel_darker` (canvas.rs:1951), and `preset_card` also fills with `panel_darker` (new_document.rs:269). Cards are the same colour as the Home background today.
   - The top bar is the global app_bar and tab strip; a Home-only colour needs a branch on `menus::home_showing` (used at chrome.rs:44).
3. **New Document dialog** (window and tabs #323232, left #252525, hero #2f2f2f, details #323232, inputs #252525, dropdowns #2f2f2f):
   - Window fill is `t.panel` in the shared modal (modal.rs:32), used by every dialog. The left column has no fill (new_document.rs:189), and the details column is `panel_darker` (196).
   - Inputs and dropdowns come from the global extreme_bg_color and the widget inactive fill.
   - The tab underline is `t.accent`, hard-wired in the shared `tab_bar` (widgets.rs:1754). Five other dialogs use it: export_for_screens.rs:259, revolve.rs:68 and 143, document_setup.rs:47, save_for_web.rs:348. A white underline therefore needs a parameter.
   - The secondary pill outline uses text_dim (widgets.rs:108).
   - Fix: a scoped `ui.visuals_mut()` override inside `new_document::show` (179-207), plus dialog tokens.
   - There is no hero card today. Cards draw a white page thumbnail (278-279), not an outline icon.
   - Existing Lucide icons that fit: printer, monitor, globe, image, palette, brush, file-plus, history, save, star, frame. Missing: smartphone, film, video, clapperboard, file, bookmark, clock. Adding any needs an SVG, an ASSETS.md row and an icon_data.rs regeneration.
   - VectorCraft's categories are Recent and Saved (newdoc.rs:503) plus Mobile, Web, Print, Film & Video, Art & Illustration, Branding, Social (engine/src/cmd/newdoc.rs:395-484). There is no "Photo" category.
4. **Inheritance pitfall:** new Tokens fields need values in all four arms, because MediumLight and Light inherit `..base` (theme.rs:194, 219). Otherwise dark dialog colours appear in the light themes.
5. **External crate:** how WidgetPalette maps the five colours to egui's weak_bg_fill and fg strokes, and DockStyle's other colours, live in craft-libs. Only post-overrides (theme.rs:318-321) are local.
6. **Canvas and hard-coded literals:**
   - Black active-artboard outline (canvas.rs:381) and black page shadow (207-208) vanish on #282828 wherever the page isn't white.
   - Canvas Color preference greys (prefs_dialog.rs:95-98).
   - Popup and window shadows (theme.rs:310-311).
   - egui's `Visuals::dark()` defaults for anything not overridden (theme.rs:298).

## 8. Screenshots, build and test commands
**Run the app with the control channel:**
`cargo run --release -p vectorcraft -- --control 7979 [file]` (CLAUDE.md:51). Use `VECTORCRAFT_NO_PREFS=1` for agent runs (development.md:83) and a separate `CARGO_TARGET_DIR` (CLAUDE.md:57).

Send JSON lines to 127.0.0.1:7979 (methods: control.rs:3-25), for example:
1. `{"id":1,"method":"ui.set","params":{"brightness":"mediumDark"}}`
2. `{"id":2,"method":"engine.execute","params":{"command":"file.newDialog"}}` — opens New Document (menus.rs:168, 953). Use `app.home` for the Home screen (menus.rs:169, 957).
3. `{"id":3,"method":"ui.screenshot","params":{"path":"/abs/shot.png"}}` (control.rs:17, 319, 381).

`ui.screenshot` needs a presented frame (CLAUDE.md:53). `/usr/bin/Xvfb` and `xvfb-run` exist in this container; whether a GL/wgpu adapter works under them is unverified.

**Headless capture:**
- `CRAFT_UI_VISUAL_FIXTURES=/abs/dir cargo test -p vectorcraft-ui-egui capture_chrome_visual_fixtures` renders the app bar and status bar for each brightness × width (800, 1280) × scale (1, 1.5, 2) to PNG (chrome.rs:1117-1170; W:1280). It needs a wgpu adapter (egui_kittest wgpu feature, ui-egui Cargo.toml:37).
- Docking captures: `CRAFT_UI_DOCKING_FIXTURES` (panel_docking_tests.rs:139, 254) and `CRAFT_UI_DOCKING_SNAPSHOT_DIR` (:468).
- There is no fixture for New Document or Home; one would need to be added.

**Quality gates:** `cargo xtask ci` (xtask/src/main.rs:175-206) runs, in order:
1. `cargo fmt --all -- --check`
2. `cargo clippy --workspace --all-targets -- -D warnings` (the no-panic lints are in Cargo.toml:92-101; clippy.toml allows unwrap in tests)
3. `cargo test --workspace`
4. `cargo xtask assets`, `cargo xtask brands`, `cargo xtask layers`
5. `cargo xtask wasm`, which is `cargo check --target wasm32-unknown-unknown -p <each>` and needs `rustup target add wasm32-unknown-unknown`

Quick loop: `cargo test -p vectorcraft-ui-egui`. rustfmt max_width is 150 (rustfmt.toml).

CLAUDE.md:20 says `cargo xtask cleanroom` runs in ci, but there is no such subcommand in xtask/src/main.rs:44-56. This is doc drift.

**Fonts:** `CRAFT_FONTS_DIR` is **optional**. Everything must build, test and run without it (CLAUDE.md:31; development.md:109-131). The Latin UI fonts are embedded with include_bytes from `assets/fonts` (theme.rs:256-258). `CRAFT_FONTS_REQUIRED=1` is for release builds only, and Japanese-glyph tests skip without the fonts.

## Key locations
- /tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft/crates/ui-egui/src/theme.rs:41 Tokens struct: all 38 UI colour fields
- /tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft/crates/ui-egui/src/theme.rs:101 base (Dark) token values, inherited by every level via ..base (accent 116, accent_strong 117)
- /tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft/crates/ui-egui/src/theme.rs:147 MediumDark (default) overrides: where the Photoshop palette should land
- /tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft/crates/ui-egui/src/theme.rs:295 theme::apply: egui Visuals from tokens, WidgetPalette (313), stroke overrides (318-321)
- /home/user/vectorcraft/crates/ui-egui/src/theme.rs:357 W-only test slider_rails_show_on_every_panel: |button_border.r - panel.r| >= 24
- /tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft/crates/ui-egui/src/chrome.rs:217 control bar uses t.panel (also status bar 504, hint bar 825); app bar t.app_bar at 32; doc tab strip t.tab_strip at 374
- /tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft/crates/ui-egui/src/chrome.rs:1117 capture_chrome_visual_fixtures (CRAFT_UI_VISUAL_FIXTURES) headless PNG capture per brightness
- /tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft/crates/ui-egui/src/canvas.rs:1950 Home screen bg = panel_darker; buttons/preset cards below
- /tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft/crates/ui-egui/src/canvas.rs:381 hard-coded black/grey artboard outline (vanishes on #282828 pasteboard)
- /tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft/crates/ui-egui/src/canvas.rs:1166 rulers: t.ruler fill, t.ruler_tick ticks and labels
- /tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft/crates/ui-egui/src/widgets.rs:91 primary_button (accent_strong pill, WHITE label) and secondary_button (103, text_dim outline)
- /tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft/crates/ui-egui/src/widgets.rs:1738 tab_bar: accent underline hard-wired; shared by 6 dialogs
- /tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft/crates/ui-egui/src/dialogs/new_document.rs:179 New Document show(): layout, details column panel_darker (196), presets (210), preset_card (264), details (295)
- /tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft/crates/ui-egui/src/dialogs/modal.rs:32 shared modal window fill = t.panel (all dialogs)
- /tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft/crates/ui-egui/src/prefs_dialog.rs:93 Canvas Color pref overrides pasteboard (apply_runtime 104-133)
- /tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft/crates/engine/src/lib.rs:936 defaults ui_brightness mediumDark, canvas_color matchUi
- /tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft/crates/engine/src/cmd/newdoc.rs:395 New Document preset CATEGORIES (Mobile, Web, Print, Film & Video, Art & Illustration, Branding, Social)
- /tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft/crates/ui-egui/src/control.rs:3 control channel methods incl. ui.set brightness (257), ui.screenshot (319)
- /tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft/xtask/src/main.rs:175 cmd_ci steps: fmt, clippy -D warnings, test, assets, brands, layers, wasm
- /tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft/CLAUDE.md:15 clean-room and asset rules (15-34), Tokens rule (45), screenshot workflow (51-53)
- /tmp/claude-0/-home-user-uploader-convertize/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/vectorcraft/xtask/src/brands.rs:18 vendor-name DENY list for user-visible strings

## Open questions
- Should the palette go into MediumDark (the default, which already has #535353/#424242), into the Dark level, or into both? If Dark, it needs its own match arm, because editing `base` leaks into the light levels.
- Is it OK under CLAUDE.md:15-20 (the owner's absolute clean-room rule against measuring Adobe apps) to use hex values measured from the user's own Photoshop screenshots? theme.rs:146 already says its values were measured from Illustrator. The screenshots must never be committed (CLAUDE.md:34), and comments and strings should say 'the reference app'.
- Inputs at #737373 give 3.59:1 contrast with #e0e0e0 text, and #a0a0a0 dim text on #535353 gives 2.94:1. Keep the measured values, or adjust for legibility?
- Which copy will be edited: /home/user/vectorcraft (the user's fork, 0a33cff Release 0.11.0, newer and with an extra colour test) or the upstream clone? Line numbers differ in chrome.rs, canvas.rs, widgets.rs and prefs_dialog.rs.
- Should the darker New Document and Home palette also apply when the user picks MediumLight or Light? New token fields need explicit light values either way.
- Hero-card wording and new headings need original text (not 'Let's start something new.') and translations in 14 catalogs: who supplies them? VectorCraft has no 'Photo' preset category; confirm we keep the app's own categories.
- craft-ui WidgetPalette and DockStyle internals (craft-libs rev 5c874d5) were not available offline, so their derived egui colours are unverified.