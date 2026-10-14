PhotoCraft colour and theme map (read-only; nothing was built or changed, and cargo was not run)

0. Which checkout
- I mapped the scratchpad clone (storytold/photocraft @ 99e1138, 2026-10-13). The user's working copy /home/user/photocraft is a different repo: a one-commit fork (izaqueotaviano/photocraft, c699e3c "Release 0.9.0", 2026-10-14).
- These files are byte-identical in both, so their line numbers hold in the working copy: theme.rs, new_doc_ui.rs, widgets.rs, panels.rs, rulers.rs, prefs_ui.rs, dialogs.rs, icons.rs, tab_strip.rs, menus.rs, chrome_ui.rs, examples/snapshot.rs, ATTRIBUTION.md, docs/ui-design.md, docs/ui-dialogs.md, docs/contributing.md.
- Three cited files have shifted lines in the working copy:
  - canvas.rs: +2 lines after about line 700 (for example LAYER_EDGES moves 830 -> 832, pro_tabs fill 2407 -> 2409, start_screen 2627 -> 2629).
  - lib.rs: +12 (the backdrop line moves 1842 -> 1854).
  - control.rs also differs.
- craftrules (../craftrules) is not present anywhere. craft-fonts is present at <scratchpad>/craft-fonts (it has fonts/manifest.txt). The toolchain is in /root/.cargo/bin; the workspace needs Rust 1.95, edition 2024 (Cargo.toml:8,10).

1. Rules that constrain UI, colour, icon and asset work (quoted)
- AGENTS.md:64 "Clean-room. We studied Photoshop and other proprietary editors for *behaviour and look only*. Never copy their code, shaders, profiles or assets ... Third-party assets must be permissively licensed, keep their license file next to them, and get a row in `ATTRIBUTION.md` ... in the same change; so do original assets." Also: "Never commit font files".
- AGENTS.md:66 "The UI is thin and data-driven ... Colours and radii come from `theme::Tokens`, never hard-coded."
- AGENTS.md:67 "Verify UI changes visually. Render offscreen with `cargo run -p photocraft-ui-egui --example snapshot` ... or launch with `--control` and take `ui.screenshot`. Look at the PNG."
- AGENTS.md:62 "Everything is a command." Any new New Document behaviour (artboards, profile, pixel aspect) must go through engine commands.
- AGENTS.md:63 "Never assume sRGB."
- AGENTS.md:53 is the no-panic rule.
- AGENTS.md:91-105 is the finish checklist (test, clippy -D warnings, xtask layers, xtask wasm).
- docs/contributing.md:5 "do not copy code, shaders, icons, ICC profiles or other assets from proprietary software (such as Photoshop). Match behaviour and look by observation and public specs ... list every asset in `ATTRIBUTION.md`."
- docs/contributing.md:11 "UI: use `theme::Tokens` and `widgets::*`. Verify visually ... attach before/after screenshots to PRs."
- docs/ui-design.md:30 "Colours and radii come from tokens. Read them with `Tokens::get(ctx)`; never hard-code a colour in a widget."
- docs/ui-design.md:31 lists the shared widgets in widgets.rs.
- docs/ui-design.md:33 "Icons: Lucide SVGs in `assets/icons` (ISC licence), embedded via `icon_data.rs`. Regenerate that file when you add icons." The recipe is at ui-design.md:42-50.
- docs/ui-design.md:40 "Verify every visual change with `ui.screenshot`, at several window sizes and in every theme."
- docs/ui-design.md:219-220 and the ja.tsv header: translations are clean-room.
- docs/ui-design.md:224-225: a test fails when a `tl!` literal is missing from any language marked complete_menus. That is 20 catalogs (i18n/mod.rs:191-222), so every new New Document string needs 20 translations.
- ATTRIBUTION.md:3-7 says every non-code asset needs a row. ATTRIBUTION.md:29 counts the Lucide icons ("113 files"), so the count must change when icons are added. There is no save, printer, smartphone or film icon in assets/icons yet.
- docs/ui-dialogs.md:143 "`fields` is the automation contract."
- docs/ui-dialogs.md:148 "Use `dialog_buttons`" (platform order: on Windows/Linux the default button comes first, widgets.rs:1121-1131).
- docs/ui-dialogs.md:149 sets New Document at 800 pt wide.
- docs/ui-dialogs.md:151 "Transparent backdrop".
- docs/ui-dialogs.md:160 is select-all on focus.

2. Where colours are defined
- crates/ui-egui/src/theme.rs is the only palette source.
  - `ThemeKind` (theme.rs:26-55) has 14 kinds. The default is `ProMedium` (theme.rs:30-32). There are four Pro brightness levels: Pro #323232, ProMedium #535353, ProLightGray #B8B8B8, ProLight #F0F0F0 (theme.rs:16-17, 28-36). `is_pro` is at theme.rs:113.
  - `Tokens` (theme.rs:142-197) has these colour roles: chrome, canvas, canvas_dot, dock, card, card_border, field, field_border, hover, pressed, text, text_dim, text_faint, icon, accent, accent_soft, accent_border, accent_text, separator, shadow, primary_bg, primary_text, danger, warning, tab_strip, row_selected, histogram_bg, caption_close(_text), scrim. Shape fields are radius_sm, radius, radius_lg. Flags are bevel, pro, round_chips.
  - `Tokens::for_kind` (theme.rs:205-746) holds the values:
    - ProMedium (theme.rs:207-227) is commented "Sampled from Photoshop 2026's default brightness". It overrides chrome 83, dock 66, card 83, card_border 66, field 69, field_border 104, hover 98, pressed 112, text 238, text_dim 212, text_faint 160, icon 226, accent_soft 110, separator 62, tab_strip 74, row_selected 107.
    - Everything else in ProMedium is inherited from Pro via `..Tokens::for_kind(ThemeKind::Pro)` (theme.rs:226).
    - Pro (theme.rs:278-317): canvas 40, accent and accent_border #378ef0, primary_bg #378ef0, radii 3/4/6, pro=true.
    - Eleven themes are full struct literals (theme.rs:278, 318, 358, 398, 441, 481, 527, 577, 620, 662, 705). Adding a token field means editing all 11, plus the live-override list (theme.rs:1467-1497).
  - `Tokens::get` (theme.rs:749-751) reads ctx temp data under the id "photocraft-theme". It falls back to Studio, not ProMedium.
  - Derived colour helpers:
    - field_selection(): hard grey 96/201 for Pro (theme.rs:807-809).
    - dark() (theme.rs:811-822).
    - layer_label_colors and the label icon grey 226 (theme.rs:764-786).
    - canvas_bg() (theme.rs:1066-1068).
- egui Visuals are built in `theme::apply` (theme.rs:974-1057):
  - panel_fill=chrome, window_fill=card, window_stroke=card_border, extreme_bg (TextEdit)=field, faint_bg=card, override_text=text, hyperlink=accent.
  - selection.bg = accent in Pro (theme.rs:995).
  - Widget fills: noninteractive=card; inactive=field/field_border; hovered=hover; active=pressed/accent_border; open=hover (theme.rs:1001-1019).
  - Fonts: Body and Button 12 pt in Pro (theme.rs:1022-1029).
  - The same style is copied to both the light and dark egui themes (theme.rs:1054-1056).
  - The menu override for Pro is in widgets.rs:17-35: hover = accent, text hard-coded WHITE (widgets.rs:30), square corners.
- Live tuning without recompiling: in debug builds only, set `PHOTOCRAFT_THEME_FILE=tokens.json` (theme.rs:1382-1500, docs/development.md:122-130). Keys are Tokens field names, values "#rrggbb" or "#rrggbbaa".
- Where each screen region gets its colour:
  - Title bar: chrome (panels.rs:581).
  - Left toolbar: chrome (panels.rs:91).
  - Options bar: chrome (panels.rs:928).
  - Status bar: chrome (panels.rs:1606).
  - Right rail: chrome (panels.rs:1678).
  - Rulers: chrome, with separator lines and text_faint ticks (rulers.rs:335-342).
  - Dock behind panels: dock (panels.rs:1748).
  - Panel tab row: tab_strip (widgets.rs:207).
  - Panel body: card (widgets.rs:219).
  - Active panel tab: card (tab_strip.rs:223).
  - Pro document tab strip: tab_strip (canvas.rs:2407). Selected document tab: chrome (canvas.rs:2436). Hovered tab: hover×0.35. Accent focus stroke at canvas.rs:2442.
  - Pasteboard: the CentralPanel backdrop, which is the `interface.canvasColor` preference or t.canvas (lib.rs:1842-1843; presets in prefs_ui.rs:73-84).
  - Home screen: drawn straight on that backdrop with dots, with no card fill (canvas.rs:2627-2682).
  - Selected layer/history row: row_selected.
  - Icon buttons: selected = accent_soft fill + accent_border stroke + accent_text icon; hover = hover (icons.rs:155-170, 185-194).
  - Buttons (widgets.rs:1195-1247): in Pro they are pills (radius = h/2). Primary = primary_bg filled, darkened ×0.9 on hover and ×0.8 on press. Secondary = 1.5 px outline in text_dim (text when hovered). Label font is theme::medium(13) (widgets.rs:1189). Height is 28 in Pro (widgets.rs:1190).
  - Dialog window: egui::Modal default frame, so window_fill = card (dialogs.rs:176). Only the colour picker passes its own frame (dialogs.rs:177-179).

3. Theme preference
- Preference fields (crates/engine/src/prefs.rs:246-300): `interface.appearanceMode` auto|dark|light (default dark, prefs.rs:59, 294); `darkTheme` (default proMedium, prefs.rs:60, 295); `lightTheme` (default proLight, prefs.rs:296); `favoriteThemes`; `canvasColor` default|black|darkGray|mediumGray|lightGray|custom with `canvasCustomColor` "#282828" (prefs.rs:62, 254-256, 298-299); `showCanvasDots`.
- Mapping to a theme: selected_theme (prefs_ui.rs:86-113). The header button cycles Auto -> Light -> Dark (prefs_ui.rs:115-129). Dark options are proMedium, pro, studio, solarizedDark, adwaitaDark, breezeDark, softDark (prefs_ui.rs:140-148); light options are at prefs_ui.rs:131-139.
- Window › Theme commands are `window.theme.<id>` and `ui.set {theme}` takes the same ids (theme.rs:92-111, docs/control-protocol.md:50). Behaviour is documented at docs/ui-design.md:22-24.
- Photoshop's four brightness shades map to Pro, ProMedium, ProLightGray and ProLight.

4. Hard-coded Color32 outside the theme
- In crates/ui-egui/src excluding theme.rs, `grep -rno 'Color32::'` finds 604 occurrences on 552 lines across 99 files. A stricter literal-constructor regex finds 598, or 538 without TRANSPARENT. For comparison, theme.rs has 409 and apps/ has 0.
- Worst files (occurrences): canvas.rs 62, widgets.rs 34, adjust_editors.rs 33, lib.rs 27, panels.rs 24, transform_tool.rs 20, channel_view.rs 18, gradient_ui.rs 17, color_range_ui.rs 16, pixel_grid.rs 13, liquify_ui.rs 12, analysis_ui.rs 12.
- Almost all of these are not window chrome and should stay:
  - canvas overlays such as black/white ant and handle pairs (canvas.rs:4130-4703);
  - about 55 image tints of WHITE;
  - pixel or channel conversions (lib.rs:2386-2395);
  - test assertions.
- The ones that do touch chrome:
  - Pro menu hover text WHITE (widgets.rs:30);
  - slider knob grey 236/40 (widgets.rs:988-991);
  - checker 250/214 (widgets.rs:1548-1585);
  - LAYER_EDGES #2d8ceb (canvas.rs:830);
  - document drop shadow (canvas.rs:2964) and image border grey 20 (canvas.rs:3674);
  - pasteboard presets (prefs_ui.rs:78-82);
  - field_selection greys (theme.rs:808);
  - the Studio-only violet wash (panels.rs:105-118);
  - type thumbnail greys (panels.rs:3047-3048);
  - Breeze close constants (titlebar.rs:27-28).

5. Tests that pin colours (`cargo test -p photocraft-ui-egui`)
- theme.rs:1211 asserts ProMedium card == rgb(83,83,83). It will fail if card becomes #4d4d4d.
- theme.rs:1183-1184 requires the four Pro levels' card.r to strictly increase (50 < 83 < 184 < 240). A #4d4d4d card (77) still passes.
- theme.rs:1160-1181 pins ProLightGray/ProLight card = chrome = 184/240 and checks contrast. It covers only those two themes; ProMedium has no contrast test.
- theme.rs:1194-1197 pins field_selection greys 96/201.
- theme.rs:1217-1241 checks style stability across OS appearance changes (structural, not values).
- Relative assertions that follow the tokens automatically: prefs_ui.rs:2177-2180, smart_ui.rs:385,397.
- crop_shield.rs:222-227 and crop_mode.rs:676 use a literal canvas 40 only as input, so they are unaffected.
- Theme-loop geometry tests (no colours): rulers.rs:466, status_bar_tests.rs:40,91, color_tab_theme_tests.rs, and the compact_visual_regressions module (panels.rs:5616).
- New Document UI tests (new_doc_ui.rs:768-1538) run in ThemeKind::ALL[0] = Pro (new_doc_ui.rs:1172) and rely on layout, so a redesign can break them:
  - SpinButton order must stay Width=0, Height=1, Resolution=2 (new_doc_ui.rs:1187-1190).
  - Category tabs are found by label, including all 8 names and the PointingHand cursor (new_doc_ui.rs:1523-1536).
  - Preset titles must stay painted text shapes with the exact title (1222-1232).
  - Double-click on a card creates the document (1234-1243).
  - Card titles must fit 152 pt in every language (882-894; tied to card width 164 at 544).
  - new_doc_remember_tests.rs depends on the field names.

6. Token mapping for the default dark theme (ProMedium)
Override these in the ProMedium block (theme.rs:208-227) so Pro (Dark) is unaffected. Each entry gives the current value, the target from the palette, and notes.
- chrome #535353 -> #535353 (keep). Covers the top bar, options bar and left toolbar. Rulers and status bar also use it today; see section 7.
- card #535353 -> #4d4d4d (panels).
  - This also changes every dialog, popup and menu fill (window_fill, theme.rs:982) and the active panel tab.
  - Update the test at theme.rs:1211.
- dock #424242 -> #424242 (keep).
- tab_strip #4a4a4a -> #424242. Covers both the document tab strip (canvas.rs:2407) and the panel tab row (widgets.rs:207).
- card_border #424242 -> keep.
- canvas (inherited) #282828 -> #282828 (keep). canvas_dot equals canvas, so the dots stay invisible.
- row_selected #6b6b6b -> #6b6b6b (keep).
- field #454545 -> "#737373-ish" per the brief. Caution:
  - #e0e0e0 text on #737373 is about 3.6:1, and #eeeeee on it about 4.1:1; both are below AA.
  - field also fills TextEdits (theme.rs:984), dropdown and widget bg (theme.rs:1008) and preset cards (new_doc_ui.rs:565).
  - #737373 may really be field_border (now #686868).
- text #eeeeee -> #e0e0e0. Caution: on row_selected #6b6b6b this drops to about 4.0:1 (today 4.6:1).
- text_faint #a0a0a0 -> #a0a0a0 (already matches the dim text).
- text_dim #d4d4d4 -> keep (or about #c8c8c8). Pro secondary button outlines use it.
- icon #e2e2e2 -> about #e0e0e0.
- hover #626262 and pressed #707070 -> keep. #e0e0e0 on #626262 is about 4.6:1.
- accent and accent_border (inherited) #378ef0 -> #2680eb. Also changes:
  - Pro selection fill (theme.rs:995);
  - menu hover;
  - focus rings;
  - selected tool and icon outline (icons.rs:160,191);
  - drop lines;
  - the selected preset card outline (new_doc_ui.rs:569).
- primary_bg (inherited) #378ef0 -> #1273e6. White text contrast goes from about 3.3:1 to about 4.55:1.
- primary_text WHITE -> keep.
- separator #3e3e3e -> keep (or #424242).
- accent_soft #6e6e6e, accent_text WHITE, shadow, scrim, danger, warning, histogram_bg, caption_close -> keep.
- Radii 3/4/6 -> keep, since this is a colours-only change.
- Doc updates if values change: docs/ui-design.md:7-8 and the theme.rs:207 comment.

7. What tokens alone cannot do (code or new tokens needed)
- Rulers #474747 and status bar #4b4b4b. Both read t.chrome (rulers.rs:335, panels.rs:1606). This needs new fields (ruler, status_bar) or methods in the style of field_selection().
- Panels #4d4d4d versus dialog and popup windows. These share card. If dialogs must stay #535353, or follow the New Document palette, a separate window token or a custom frame is needed.
- Home screen (#1e1e1e background, #323232 top bar, #2c2c2c cards, #1372e6 button). The backdrop is canvas/pasteboard (lib.rs:1842), which must stay #282828, and there is no card fill today (canvas.rs:2634-2681). This needs a new token plus a painted card, which is a layout change.
- New Document dialog palette (window and right panel #323232, left #252525, hero #2f2f2f, inputs #252525, dropdowns #2f2f2f, inactive tabs #a5a5a5).
  - The modal frame is global window_fill (dialogs.rs:176).
  - Inputs and dropdowns both come from `field` (theme.rs:984, 1008).
  - Tokens are global ctx data (theme.rs:749-751, 979), and there is no scoped-override mechanism.
  - Route: render this dialog with Pro-dark-derived tokens, which almost match (chrome/card #323232 theme.rs:280/284, field #242424 theme.rs:286, dock #1e1e1e theme.rs:283). Swap the ctx token data and `ui.visuals_mut()` around new_doc_ui::body, and give the modal its own frame as the colour picker does (dialogs.rs:177-179).
  - Risk: verify that egui 0.36 ComboBox popups use the scoped style rather than the global one.
- Inside new_doc_ui::body (new_doc_ui.rs:497-765), these are code changes, not token changes:
  - Primary label weight: medium(13), not semibold (widgets.rs:1189).
  - Selected card: 1.5 px accent stroke on a row_selected fill (new_doc_ui.rs:557-570). The target is a 2 px #2680eb outline.
  - Active tab underline is a 2 px t.text line; inactive tabs are text_dim (new_doc_ui.rs:508-511).
  - Saved is chained last (new_doc_ui.rs:504), not second.
  - The section label reads "BLANK DOCUMENT PRESETS ({n})" (542). "YOUR RECENT ITEMS" and the hero card are new strings.
  - No Artboards checkbox, no Advanced Options and no save-preset icon exist yet. Save Preset… is a text button (452-495).
  - file.new accepts only width, height, mode, depth, background, backgroundColor, resolution and name (engine/src/commands.rs:402-406). Profile, pixel aspect and artboard would have to chain the existing commands edit.assignProfile, view.pixelAspectRatio.* and layer.new.artboard (all present in engine/menu_catalog). Otherwise they become dead settings.
  - Button order: dialog_buttons puts Create before Close on Windows/Linux (widgets.rs:1121-1131; dialogs.rs:364-386, 417). Close then Create in the bottom-right only happens on macOS.
  - Width is fixed at 800 (dialogs.rs:198-207).
- Reusable translations already exist for "Pixel Aspect Ratio", "Advanced", "Save Preset…", "Recent" and "Saved" (20/20 catalogs), and "Color Profile" (15/20). "Artboards" is in 8/20. "Advanced Options" and the hero wording are in 0/20.

8. Screenshots
- Offscreen, with no window (docs/development.md:403-417; examples/snapshot.rs:1-22). It starts in the default theme, ProMedium (snapshot.rs:71):

  cargo run --release -p photocraft-ui-egui --example snapshot -- --out nd.png --size 1440x900 --scale 2 --script '[["ui.set",{"theme":"proMedium"}],["ui.menu.invoke",{"id":"file.new"}]]'

  - `ui.menu.invoke file.new` with no params opens the dialog (menus.rs:293-296). `ui.dialog.open {"kind":"newDocument"}` also works (control.rs:780-782, docs/control-protocol.md:61).
  - Leave out --open to capture the Home screen; --open img to capture the main window.
  - Other flags: --system-theme, --custom-titlebar, --click-at.
- Live: `cargo run --release -p photocraft -- --control 7878 --control-token-file .private/control.token --automation-read-root work --automation-write-root work`. Then send the auth JSON line followed by `{"method":"ui.screenshot","params":{"path":...}}` over nc (docs/development.md:38-40, 132-147).
- Compact visual fixtures across every theme: `CRAFT_UI_VISUAL_FIXTURES=/tmp/x cargo test -p photocraft-ui-egui --lib compact_visual_regressions -- --nocapture` (docs/ui-design.md:113-115).

9. Build, test and lint commands
- Fonts input: `CRAFT_FONTS_DIR="$PWD/../craft-fonts"` must be an absolute path (AGENTS.md:64, docs/development.md:72-77). Here that is `CRAFT_FONTS_DIR=/tmp/claude-0/-home-user/e91b1203-da4e-5e42-9cdb-6a036b7511c0/scratchpad/craft-fonts`. CI adds `CRAFT_FONTS_REQUIRED=1`.
- HEIF is an opt-in feature: `--features heif` (apps/photocraft/Cargo.toml:10-13; crates/codecs/Cargo.toml:16-19; crates/io/Cargo.toml:15-16).
- CI (.github/workflows/ci.yml):
  - `cargo fmt --all -- --check` (116)
  - `cargo test --workspace --locked --features heif` (120, 146)
  - `cargo clippy --workspace --all-targets --locked --features heif -- -D warnings` (149)
  - `cargo xtask layers` (152)
  - `cargo xtask scorecard --check` (158)
  - `cargo xtask wasm` (206)
- Local per-crate gate (AGENTS.md:93-98, 107):
  - `cargo test -p photocraft-ui-egui --lib --tests` (fast loop) or `cargo test -p photocraft-ui-egui`
  - `cargo clippy -p photocraft-ui-egui --all-targets -- -D warnings`
  - `cargo xtask layers`
  - `cargo xtask wasm` (ui-egui is L6)
  - `cargo xtask ci` bundles fmt, clippy, tests, layers and wasm.
- Parallel agents should use `CARGO_TARGET_DIR=target/agent-<name>` (AGENTS.md:117).

## Key locations
- crates/ui-egui/src/theme.rs:142 Tokens struct: every colour role
- crates/ui-egui/src/theme.rs:208 ProMedium tokens (default dark theme), sampled from PS 2026; inherits Pro via ..Tokens::for_kind(Pro) at line 226
- crates/ui-egui/src/theme.rs:278 Pro (Dark) tokens: canvas #282828, accent and primary #378ef0, chrome/card #323232, field #242424, dock #1e1e1e (close to the New Document palette)
- crates/ui-egui/src/theme.rs:749 Tokens::get: global ctx temp data (fallback Studio); no scoped override
- crates/ui-egui/src/theme.rs:974 apply(): builds egui Visuals from tokens (panel_fill=chrome, window_fill=card, extreme_bg=field, selection=accent)
- crates/ui-egui/src/theme.rs:1211 Test pinning ProMedium card == rgb(83,83,83)
- crates/ui-egui/src/theme.rs:1183 Test: the four Pro levels' card brightness must strictly increase
- crates/ui-egui/src/theme.rs:1382 PHOTOCRAFT_THEME_FILE live token overrides (debug builds)
- crates/ui-egui/src/widgets.rs:1200 button_impl_h: Pro pill buttons (primary = primary_bg fill, secondary = text_dim outline); label font medium(13) at 1189
- crates/ui-egui/src/widgets.rs:28 Pro menu hover = accent with hard-coded WHITE text
- crates/ui-egui/src/widgets.rs:207 Panel tab row = t.tab_strip; body = t.card (219)
- crates/ui-egui/src/panels.rs:1606 Status bar fill = t.chrome (no own token)
- crates/ui-egui/src/rulers.rs:335 Ruler background = t.chrome (no own token)
- crates/ui-egui/src/canvas.rs:2407 Pro document tab strip = t.tab_strip; selected tab = t.chrome (2436)
- crates/ui-egui/src/canvas.rs:2627 Home/start screen drawn on the pasteboard backdrop, no card fill
- crates/ui-egui/src/lib.rs:1842 CentralPanel backdrop = pasteboard pref or t.canvas (line 1854 in /home/user/photocraft)
- crates/ui-egui/src/prefs_ui.rs:73 pasteboard_color presets and selected_theme (86), dark theme options (140)
- crates/engine/src/prefs.rs:246 Interface prefs: appearanceMode/darkTheme/lightTheme/canvasColor, defaults dark + proMedium (290-300)
- crates/ui-egui/src/new_doc_ui.rs:497 New Document body: category tabs, preset grid, Preset Details; colours at 508-511, 557-576
- crates/ui-egui/src/new_doc_ui.rs:1187 UI tests rely on SpinButton order Width/Height/Resolution and tab labels
- crates/ui-egui/src/dialogs.rs:176 Modal frame uses global style (window_fill=card); colour picker custom frame at 177; New Document width 800 at 198-207; Create/Close at 364-386
- crates/ui-egui/src/icons.rs:155 button_chrome: selected = accent_soft + accent_border + accent_text
- crates/engine/src/commands.rs:402 file.new params: no profile, pixel aspect or artboard
- crates/ui-egui/examples/snapshot.rs:1 Offscreen snapshot tool (--out --size --scale --script); default theme ProMedium at 71
- crates/ui-egui/src/menus.rs:293 file.new with no params opens the New Document dialog (for snapshot scripts)
- AGENTS.md:64 Clean-room, ATTRIBUTION and no-font-files rules
- docs/ui-design.md:30 Token, widget and icon rules; icon regeneration recipe at 42-50
- .github/workflows/ci.yml:149 CI clippy command with --features heif -D warnings

## Open questions
- Inputs '#737373-ish': this conflicts with the existing PS 2026-sampled field #454545 and fails AA contrast (about 3.6:1 with #e0e0e0 text). Was #737373 actually the field border or the dropdown outline?
- Text #e0e0e0 on row_selected #6b6b6b is about 4.0:1, below 4.5:1. Keep text #eeeeee, or lighten only the selected-row text?
- Should the recolour target only ProMedium (the default dark theme) or also Pro (Dark)? Changing accent and primary in the Pro block changes both.
- Panels #4d4d4d versus #535353 dialogs and menus: card also fills every dialog and popup. Add a separate window/popup token, or let dialogs darken too?
- New Document: should Close/Create follow the platform order from dialog_buttons (Create first on Windows/Linux) or Photoshop's Close-then-Create everywhere?
- Advanced Options (colour profile, pixel aspect) and Artboards: wire them to the existing commands (edit.assignProfile, view.pixelAspectRatio.*, layer.new.artboard) after file.new, or leave them out to avoid dead settings?
- Should implementation happen in /home/user/photocraft (the fork snapshot, Release 0.9.0)? Its canvas.rs, lib.rs and control.rs line numbers differ slightly from the clone mapped here.
- Need to verify that egui 0.36 ComboBox popups inherit a scoped ui style. If not, the New Document dropdown lists will use the global ProMedium visuals.