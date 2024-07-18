def buttons_gen(curr_page: int, pages: int, prev: str, next_p: str) -> list:
    buttons = [f'{curr_page}/{pages}']
    if prev:
        buttons.insert(0, 'previous')
    if curr_page > 1:
        buttons.insert(1, 'backward')
    if curr_page < pages:
        buttons.append('forward')
    if next_p:
        buttons.append('next')
    return buttons
