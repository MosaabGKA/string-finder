import flet as ft
import timeit


def brute_force_search(text, pattern):
    start_time = timeit.default_timer()
    occurrences = []
    for i in range(len(text) - len(pattern) + 1):
        j = 0
        while j < len(pattern) and text[i + j] == pattern[j]:
            j += 1
        if j == len(pattern):
            occurrences.append(i)
    end_time = timeit.default_timer()
    return occurrences, end_time - start_time


def knuth_morris_pratt_search(text, pattern):
    start_time = timeit.default_timer()
    text = pattern + "\0" + text
    text_length = len(text)
    pattern_length = len(pattern)
    prefix_function = [0] * text_length
    for i in range(1, text_length):
        j = prefix_function[i - 1]
        while j > 0 and text[i] != text[j]:
            j = prefix_function[j - 1]
        if text[i] == text[j]:
            j += 1
        prefix_function[i] = j
    occurrences = []
    for i in range(pattern_length + 1, text_length):
        if prefix_function[i] == pattern_length:
            occurrences.append(i - 2 * pattern_length)
    end_time = timeit.default_timer()
    return occurrences, end_time - start_time


def rabin_karp_search(text, pattern):
    # start_time = time.time()
    start_time = timeit.default_timer()
    prime = 127
    mod = 1000000009
    text_length = len(text)
    pattern_length = len(pattern)

    if not pattern:
        return []
    if not text:
        return []
    if pattern_length > text_length:
        return []

    prime_powers = [1] * max(text_length, pattern_length)
    for i in range(1, len(prime_powers)):
        prime_powers[i] = (prime_powers[i - 1] * prime) % mod

    text_prefix_hashes = [0] * (text_length + 1)
    for i in range(text_length):
        text_prefix_hashes[i + 1] = (
            text_prefix_hashes[i] + (ord(text[i])) * prime_powers[i]
        ) % mod

    pattern_hash = 0
    for i in range(pattern_length):
        pattern_hash = (pattern_hash + (ord(pattern[i])) * prime_powers[i]) % mod

    occurrences = []
    for i in range(text_length - pattern_length + 1):
        cur_substring_hash = (
            text_prefix_hashes[i + pattern_length] - text_prefix_hashes[i] + mod
        ) % mod

        if cur_substring_hash == (pattern_hash * prime_powers[i]) % mod:
            if text[i : i + pattern_length] == pattern:
                occurrences.append(i)
    # end_time = time.time()
    end_time = timeit.default_timer()
    return occurrences, end_time - start_time


# --- Main Flet Application ---
def main(page: ft.Page):
    page.window.maximized = True
    page.title = "String Finder"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.padding = 0
    page.bgcolor = ft.Colors.GREY_50
    page.window_min_width = 1000
    page.window_min_height = 1000
    page.route = "/"

    # Theme colors
    primary_color = "#1EA1C2"
    accent_color = "#EB8039"
    dark_bg = "#1E293B"
    light_bg = "#FFFFFF"

    # --- Theme Toggle Functionality ---
    def switch_theme(e):
        page.theme_mode = (
            ft.ThemeMode.DARK
            if page.theme_mode == ft.ThemeMode.LIGHT
            else ft.ThemeMode.LIGHT
        )
        theme_icon.icon = (
            ft.Icons.LIGHT_MODE
            if page.theme_mode == ft.ThemeMode.LIGHT
            else ft.Icons.DARK_MODE
        )
        main_content.bgcolor = (
            ft.Colors.GREY_900
            if page.theme_mode == ft.ThemeMode.DARK
            else ft.Colors.GREY_50
        )
        if highlight_area.controls and isinstance(
            highlight_area.controls[0], ft.Container
        ):
            highlight_area.controls[0].bgcolor = (
                ft.Colors.GREY_900
                if page.theme_mode == ft.ThemeMode.DARK
                else ft.Colors.GREY_100
            )
        page.update()

    # --- Sidebar Definition ---
    theme_icon = ft.IconButton(
        icon=ft.Icons.LIGHT_MODE,
        on_click=switch_theme,
        tooltip="Toggle Theme",
        icon_size=30,
        style=ft.ButtonStyle(
            shape=ft.CircleBorder(),
            padding=10,
        ),
    )

    sidebar = ft.Container(
        width=350,
        height=850,
        padding=20,
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_center,
            end=ft.alignment.bottom_center,
            colors=["#0D6E8C", primary_color],
        ),
        content=ft.Column(
            [
                ft.Image(
                    src="icon.svg",
                    width=250,
                    height=250,
                    border_radius=20,
                    fit=ft.ImageFit.COVER,
                ),
                ft.Text(
                    "String Finder",
                    size=26,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE,
                ),
                ft.Divider(color=ft.Colors.WHITE54, height=20),
                ft.Text(
                    "Search algorithms:",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE,
                ),
                ft.Text(
                    "Brute Force\nKnuth-Morris-Pratt\nRabin-Karp",
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE70,
                ),
                ft.Divider(color=ft.Colors.WHITE54, height=40),
                theme_icon,
                ft.Text("v1.0.0", color=ft.Colors.WHITE54),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
            expand=True,
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
        ),
    )

    # --- File Pickers ---
    file_picker_input1 = ft.FilePicker()
    file_picker_input2 = ft.FilePicker()
    page.overlay.extend([file_picker_input1, file_picker_input2])

    loading_text_file = ft.ProgressRing(
        width=20, height=20, stroke_width=2, visible=False
    )
    uploaded_file_text = ft.Text("", size=12, color=ft.Colors.GREY)

    loading_pattern_file = ft.ProgressRing(
        width=20, height=20, stroke_width=2, visible=False
    )
    uploaded_pattern_text = ft.Text("", size=12, color=ft.Colors.GREY)

    def load_text_file(e: ft.FilePickerResultEvent):
        if e.files:
            loading_text_file.visible = True
            uploaded_file_text.value = f"Loading file: {e.files[0].name}..."
            page.update()
            try:
                file = e.files[0]
                with open(file.path, "r", encoding="utf-8") as f:
                    input1.value = f.read()
                uploaded_file_text.value = f"Loaded: {e.files[0].name}"
                uploaded_file_text.color = ft.Colors.GREEN
            except Exception as ex:
                uploaded_file_text.value = f"Error: {str(ex)}"
                uploaded_file_text.color = ft.Colors.RED
            loading_text_file.visible = False
            page.update()

    def load_pattern_file(e: ft.FilePickerResultEvent):
        if e.files:
            loading_pattern_file.visible = True
            uploaded_pattern_text.value = f"Loading pattern file: {e.files[0].name}..."
            page.update()
            try:
                file = e.files[0]
                with open(file.path, "r", encoding="utf-8") as f:
                    input2.value = f.read()
                uploaded_pattern_text.value = f"Loaded: {e.files[0].name}"
                uploaded_pattern_text.color = ft.Colors.GREEN
            except Exception as ex:
                uploaded_pattern_text.value = f"Error: {str(ex)}"
                uploaded_pattern_text.color = ft.Colors.RED
            loading_pattern_file.visible = False
            page.update()

    file_picker_input1.on_result = load_text_file
    file_picker_input2.on_result = load_pattern_file

    # --- Input Fields ---
    input1 = ft.TextField(
        label="Text to Search In",
        multiline=True,
        min_lines=3,
        max_lines=3,
        border_color=primary_color,
        focused_border_color=primary_color,
        expand=True,
        text_size=14,
    )

    input2 = ft.TextField(
        label="Text to Search For",
        multiline=True,
        min_lines=3,
        max_lines=3,
        border_color=primary_color,
        focused_border_color=primary_color,
        expand=True,
        text_size=14,
    )

    # --- Algorithm Selection ---
    algorithm_group = ft.RadioGroup(
        content=ft.Column(
            spacing=10,
            controls=[
                ft.Radio(value="bruteforce", label="Brute Force"),
                ft.Radio(value="Knuth-Morris-Pratt", label="Knuth-Morris-Pratt"),
                ft.Radio(value="Rabin-Karp", label="Rabin-Karp"),
            ],
        ),
        value="bruteforce",
    )

    # --- Case Sensitivity Checkbox ---
    case_sensitive_checkbox = ft.Checkbox(label="Case Sensitive", value=True)

    # --- Result Display Elements ---
    result_text = ft.Text("Results will appear here", selectable=True)
    highlight_area = ft.Column(
        scroll=ft.ScrollMode.ALWAYS,
        expand=True,
        controls=[ft.Text("Your highlighted matches will appear here.")],
    )

    # --- Search Function ---
    def search_clicked(e):
        text = input1.value
        pattern = input2.value
        method = algorithm_group.value
        case_sensitive = case_sensitive_checkbox.value
        if not case_sensitive:
            text = text.lower()
            pattern = pattern.lower()

        if not text:
            result_text.value = "Please enter text to search in."
            result_text.color = ft.Colors.RED
            page.update()
            return

        if not pattern:
            result_text.value = "Please enter pattern to search for."
            result_text.color = ft.Colors.RED
            page.update()
            return

        if not method:
            result_text.value = "Please select an algorithm."
            result_text.color = ft.Colors.RED
            page.update()
            return

        result_text.value = "Searching..."
        result_text.color = ft.Colors.BLUE_GREY_600
        highlight_area.controls = [ft.ProgressRing(width=30, height=30, stroke_width=3)]
        page.update()

        indices = []
        try:
            if method == "bruteforce":
                indices, time_taken = brute_force_search(text, pattern)
            elif method == "Knuth-Morris-Pratt":
                indices, time_taken = knuth_morris_pratt_search(text, pattern)
            elif method == "Rabin-Karp":
                indices, time_taken = rabin_karp_search(text, pattern)
        except Exception as ex:
            result_text.value = f"Error during search: {ex}"
            result_text.color = ft.Colors.RED
            highlight_area.controls = [ft.Text("An error occurred during search.")]
            page.update()
            return

        if not indices:
            result_text.value = (
                f"No matches found in the text "
                f"({'Case-Sensitive' if case_sensitive else 'Case-Insensitive'}).\n"
                f"Time taken: {1000*time_taken:.9f} milliseconds."
            )
            result_text.color = ft.Colors.ORANGE_700
            highlight_area.controls = [
                ft.Text(
                    "No matches found in the text.", style=ft.TextThemeStyle.BODY_MEDIUM
                )
            ]
        else:
            result_text.value = (
                f"Found {len(indices)} matches using {method} "
                f"({'Case-Sensitive' if case_sensitive else 'Case-Insensitive'}).\n"
                f"Time taken: {1000*time_taken:.9f} milliseconds."
            )
            result_text.color = ft.Colors.GREEN_700

            spans = []
            last_pos = 0
            for i in sorted(indices):
                if i > last_pos:
                    spans.append(ft.TextSpan(text[last_pos:i]))

                matched_text = text[i : i + len(pattern)]
                spans.append(
                    ft.TextSpan(
                        matched_text,
                        style=ft.TextStyle(
                            bgcolor=accent_color,
                            color=ft.Colors.WHITE,
                            weight=ft.FontWeight.BOLD,
                        ),
                    )
                )
                last_pos = i + len(pattern)

            if last_pos < len(text):
                spans.append(ft.TextSpan(text[last_pos:]))

            highlight_text = ft.Text(spans=spans, selectable=True, size=14)
            highlight_area.controls = [
                ft.Container(
                    content=highlight_text,
                    padding=10,
                    border_radius=ft.border_radius.all(5),
                    bgcolor=(
                        ft.Colors.GREY_100
                        if page.theme_mode == ft.ThemeMode.LIGHT
                        else ft.Colors.GREY_900
                    ),
                )
            ]

        page.update()

    # --- Main Content ---
    main_content = ft.Container(
        expand=True,
        padding=30,
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(
                            "String Search",
                            size=28,
                            weight=ft.FontWeight.BOLD,
                            color=primary_color,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.HELP_OUTLINE,
                            tooltip="Help",
                            icon_size=20,
                            icon_color=primary_color,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(height=10),
                ft.Card(
                    content=ft.Container(
                        padding=20,
                        content=ft.Column(
                            [
                                ft.Text(
                                    "Input Text", size=18, weight=ft.FontWeight.BOLD
                                ),
                                ft.Row(
                                    [
                                        ft.ElevatedButton(
                                            "Upload Text File",
                                            icon=ft.Icons.UPLOAD_FILE,
                                            on_click=lambda _: file_picker_input1.pick_files(),
                                            style=ft.ButtonStyle(
                                                color=ft.Colors.WHITE,
                                                bgcolor=primary_color,
                                                padding=15,
                                            ),
                                        ),
                                        loading_text_file,
                                        uploaded_file_text,
                                    ],
                                    spacing=10,
                                ),
                                input1,
                                ft.Container(
                                    content=ft.Text(
                                        "Search Pattern",
                                        size=18,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    margin=ft.margin.only(top=10),
                                ),
                                ft.Row(
                                    [
                                        ft.ElevatedButton(
                                            "Upload Pattern File",
                                            icon=ft.Icons.UPLOAD_FILE,
                                            on_click=lambda _: file_picker_input2.pick_files(),
                                            style=ft.ButtonStyle(
                                                color=ft.Colors.WHITE,
                                                bgcolor=primary_color,
                                                padding=15,
                                            ),
                                        ),
                                        loading_pattern_file,
                                        uploaded_pattern_text,
                                    ],
                                    spacing=10,
                                ),
                                input2,
                            ],
                            spacing=15,
                        ),
                    ),
                    elevation=5,
                    margin=ft.margin.only(bottom=20),
                ),
                ft.Card(
                    content=ft.Container(
                        padding=20,
                        content=ft.Column(
                            [
                                ft.Text(
                                    "Algorithm Selection",
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                algorithm_group,
                                case_sensitive_checkbox,
                                ft.ElevatedButton(
                                    "Search",
                                    on_click=search_clicked,
                                    icon=ft.Icons.SEARCH,
                                    style=ft.ButtonStyle(
                                        color=ft.Colors.WHITE,
                                        bgcolor=accent_color,
                                        padding=20,
                                    ),
                                    width=200,
                                ),
                            ],
                            spacing=15,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                    ),
                    elevation=5,
                    margin=ft.margin.only(bottom=20),
                ),
                ft.Card(
                    content=ft.Container(
                        padding=20,
                        content=ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Text(
                                            "Results",
                                            size=18,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Icon(
                                            ft.Icons.INFO_OUTLINE,
                                            size=16,
                                            color=ft.Colors.GREY,
                                        ),
                                    ],
                                    spacing=10,
                                ),
                                ft.Divider(height=10),
                                result_text,
                                ft.Divider(height=10),
                                ft.Text(
                                    "Highlighted Matches:",
                                    size=14,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                highlight_area,
                            ],
                            spacing=10,
                        ),
                    ),
                    elevation=5,
                    expand=True,
                ),
            ],
            spacing=20,
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True,
        ),
        bgcolor=ft.Colors.GREY_50,
    )

    def welcome_view():
        return ft.View(
            "/welcome",
            [
                ft.Container(
                    expand=True,
                    gradient=ft.LinearGradient(
                        begin=ft.alignment.top_center,
                        end=ft.alignment.bottom_center,
                        colors=["#54A0E6", "#AFD0EC", "#C2D8ED"],
                    ),
                    content=ft.Column(
                        [
                            ft.Container(
                                content=ft.Image(
                                    src="bgimage.png",
                                    width=700,
                                    height=500,
                                    fit=ft.ImageFit.CONTAIN,
                                ),
                                margin=ft.margin.only(bottom=10),
                            ),
                            ft.Column(
                                [
                                    ft.Text(
                                        "Welcome to String Finder!",
                                        size=36,
                                        weight=ft.FontWeight.BOLD,
                                        color="#0767A2",
                                        text_align=ft.TextAlign.CENTER,
                                    ),
                                    ft.Text(
                                        "Your powerful tool for searching patterns in text using various algorithms.",
                                        size=18,
                                        color=ft.Colors.BLUE_GREY_900,
                                        text_align=ft.TextAlign.CENTER,
                                    ),
                                    ft.Container(height=15),
                                    ft.ElevatedButton(
                                        "Get Started",
                                        on_click=lambda e: page.go("/app"),
                                        icon=ft.Icons.ARROW_FORWARD,
                                        style=ft.ButtonStyle(
                                            bgcolor=accent_color,
                                            color=ft.Colors.WHITE,
                                            padding=ft.padding.all(15),
                                        ),
                                    ),
                                ],
                                spacing=5,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                        ],
                        spacing=0,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                )
            ],
            padding=0,
        )

    def main_app_view():
        return ft.View(
            "/app",
            [
                ft.Row(
                    [sidebar, main_content],
                    expand=True,
                    spacing=0,
                )
            ],
            padding=0,
        )

    def route_change(route):
        # page.views.clear()
        if page.route == "/" or page.route == "/welcome":
            page.views.append(welcome_view())
        elif page.route == "/app":
            page.views.append(main_app_view())
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)


ft.app(target=main)