# ignore W0212
# pylint: disable=W0212

import streamlit as st


def func():
    return None


def theme_toggle():
    ms = st.session_state
    if "themes" not in ms:
        ms.themes = {
            "current_theme": "dark",
            "refreshed": True,
            "light": {
                "theme.base": "dark",
                # "theme.backgroundColor": "black",
                # "theme.primaryColor": "#c98bdb",
                # "theme.secondaryBackgroundColor": "#5591f5",
                # "theme.textColor": "white",
                "button_face": "Dark Mode",
            },
            "dark": {
                "theme.base": "light",
                # "theme.backgroundColor": "white",
                # "theme.primaryColor": "#5591f5",
                # "theme.secondaryBackgroundColor": "#82E1D7",
                # "theme.textColor": "#0a1464",
                "button_face": "Light Mode",
            },
        }

    if "toggle_state" not in ms:
        ms.toggle_state = False

    def ChangeTheme():
        previous_theme = ms.themes["current_theme"]
        tdict = (
            ms.themes["light"]
            if ms.themes["current_theme"] == "light"
            else ms.themes["dark"]
        )
        for vkey, vval in tdict.items():
            if vkey.startswith("theme"):
                st._config.set_option(vkey, vval)

        ms.themes["refreshed"] = False

        if previous_theme == "dark":
            ms.themes["current_theme"] = "light"
        elif previous_theme == "light":
            ms.themes["current_theme"] = "dark"

        ms.toggle_state = not ms.toggle_state

    # Use a checkbox as a toggle switch
    toggle_label = (
        "Dark Mode" if ms.themes["current_theme"] == "light" else "Light Mode"
    )
    toggle_state = st.sidebar.toggle(
        toggle_label, value=ms.toggle_state, key="toggle_theme"
    )

    if toggle_state != ms.toggle_state:
        ChangeTheme()

    if ms.themes["refreshed"] == False:
        ms.themes["refreshed"] = True
        st.rerun()
