# gradio-app/gradio — last 2 releases



## gradio@6.28.0 — 2026-09-18

### Features

-   [#13840](https://github.com/gradio-app/gradio/pull/13840) [`aab9fcf`](https://github.com/gradio-app/gradio/commit/aab9fcf79ed77a5e5aeca8dd866b4ec94be08a70) - workflow: add styling to input nodes.  Thanks @hannahblair!
-   [#13836](https://github.com/gradio-app/gradio/pull/13836) [`abf6825`](https://github.com/gradio-app/gradio/commit/abf6825e96f9f546fa8f9d8fb378c40ad967238e) - workflow: add pending node UI.  Thanks @hannahblair!
-   [#13573](https://github.com/gradio-app/gradio/pull/13573) [`5ab610f`](https://github.com/gradio-app/gradio/commit/5ab610f1d376fc56169493495767144944ae0273) - workflow: add getting started templates.  Thanks @hannahblair!
-   [#13850](https://github.com/gradio-app/gradio/pull/13850) [`cb0cdac`](https://github.com/gradio-app/gradio/commit/cb0cdac181efea2e5f6fdec35e65829245cf5ae5) - Add keyword arguments for event inputs.  Thanks @abidlabs!
-   [#13851](https://github.com/gradio-app/gradio/pull/13851) [`afffecc`](https://github.com/gradio-app/gradio/commit/afffeccf69262a8070a091b50206c1e33b8c06c4) - Add configurable tab overflow and alignment.  Thanks @abidlabs!
-   [#13843](https://github.com/gradio-app/gradio/pull/13843) [`8193f16`](https://github.com/gradio-app/gradio/commit/8193f1644cf8e3746f1d10e5643240768169f5c0) - Speed up multipage app navigation.  Thanks @abidlabs!
-   [#13862](https://github.com/gradio-app/gradio/pull/13862) [`3353446`](https://github.com/gradio-app/gradio/commit/3353446616a56838e7e3cb3477fcd02664a0db40) - Expose live camera and slider position to event handlers.  Thanks @abidlabs!/n  `camera_position` on `gr.Model3D` and `slider_position` on `gr.ImageSlider` now follow the user, so a function whose parameter is annotated with the component reads the view that is actually on screen. Both can still be set from the backend to move the camera or the divider./n  Also fixes, in the same area:/n  - `camera_position` is applied on load for `display_mode="point_cloud"` and `display_mode="wireframe"`, not only for `"solid"`./n  - `camera_position` is applied to interactive (uploadable) `gr.Model3D`, and `slider_position` to interactive `gr.ImageSlider`; both previously ignored it./n  - `pan_speed` is passed through to the `gr.Model3D` viewer; it was silently stuck at its default./n  - A Model3D camera observer was added on every camera update without ever being removed; exactly one is now registered, and it is cleaned up with the component.

### Fixes

-   [#13829](https://github.com/gradio-app/gradio/pull/13829) [`908b427`](https://github.com/gradio-app/gradio/commit/908b427466c2ac1d2950ca3b9fb39371f167fba0) - Fix `gr.Dataframe` shift+click range selecting rows hidden by the search.  Thanks @hysts!
-   [#13847](https://github.com/gradio-app/gradio/pull/13847) [`0293306`](https://github.com/gradio-app/gradio/commit/0293306f3f25bf4cda44b6e819060edd5fcbd09e) - Encode streamed video's audio once per stream.  Thanks @hysts!
-   [#13831](https://github.com/gradio-app/gradio/pull/13831) [`d99a49a`](https://github.com/gradio-app/gradio/commit/d99a49a1456dd11efbec75b74c29657466b12b30) - Keep the empty Dataframe's add row button on screen in fullscreen.  Thanks @hysts!
-   [#13816](https://github.com/gradio-app/gradio/pull/13816) [`ca09427`](https://github.com/gradio-app/gradio/commit/ca0942761b2b276aa8fab26d076e8b1f1605fcf0) - Fix private Space file URLs in gr.load() and the JS client.  Thanks @abidlabs!
-   [#13868](https://github.com/gradio-app/gradio/pull/13868) [`efef209`](https://github.com/gradio-app/gradio/commit/efef209b6549a9e85de8521e002faa15c77e5846) - Fix deep links on Windows, and only accept a deep link that looks like one.  Thanks @dawoodkhan82!
-   [#13817](https://github.com/gradio-app/gradio/pull/13817) [`81b7b77`](https://github.com/gradio-app/gradio/commit/81b7b77787fad818d686f43fc2347b32d2ceea99) - Several fixes related to rendering of custom components.  Thanks @abidlabs!



## @gradio/workflowcanvas@0.12.0 — 2026-09-18

### Features

-   [#13840](https://github.com/gradio-app/gradio/pull/13840) [`aab9fcf`](https://github.com/gradio-app/gradio/commit/aab9fcf79ed77a5e5aeca8dd866b4ec94be08a70) - workflow: add styling to input nodes.  Thanks @hannahblair!
-   [#13836](https://github.com/gradio-app/gradio/pull/13836) [`abf6825`](https://github.com/gradio-app/gradio/commit/abf6825e96f9f546fa8f9d8fb378c40ad967238e) - workflow: add pending node UI.  Thanks @hannahblair!
-   [#13573](https://github.com/gradio-app/gradio/pull/13573) [`5ab610f`](https://github.com/gradio-app/gradio/commit/5ab610f1d376fc56169493495767144944ae0273) - workflow: add getting started templates.  Thanks @hannahblair!

### Dependency updates

-   @gradio/utils@0.14.2
-   @gradio/client@2.7.0
