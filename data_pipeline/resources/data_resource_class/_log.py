from dataclasses import dataclass

class _DataResourceLog:
    def log(self, msg: str, stdout=None, style=None, style_category="notice") -> None:
        stdout = stdout or getattr(self, '_stdout', None)
        style = style or getattr(self, '_style', None)
        if stdout:
            if style and style_category:
                try:
                    style_fn = getattr(style, style_category.upper(), None)
                    styled_msg = style_fn(msg) if style_fn else msg
                except Exception:
                    styled_msg = msg
            else:
                styled_msg = msg
            stdout.write(styled_msg + "\n")
        else:
            print(msg)

    def stage_status_message(self, stage: str, stage_status: str, **kwargs) -> None:
        BOLD, RESET = "\033[1m", "\033[0m"
        stage_u = stage.upper()
        stage_status_u = stage_status.upper()
        self.log(f"{BOLD}[{stage_u} STAGE {stage_status_u}]{RESET}", **kwargs)

    def mark_section(self, symbol = "-") -> None:
        self.log(symbol * 100)

    def stage_status_banner(self, stage: str, stage_status: str, **kwargs) -> None:
        self.mark_section("=")
        self.stage_status_message(stage, stage_status, **kwargs)
        self.mark_section("=")

    
    