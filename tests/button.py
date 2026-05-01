import charmy as cm


window = cm.Window(size=(300, 160))
window.title = "Button test"

test_line = cm.shape.PolyLine([
    (10, 10), (50, 150), (200, 300), (30, 30)
    ])
test_line.draw(window, cm.texture.Color((255, 0, 0)))

# button = cm.Button()
# window.bind("mouse_press", lambda e: print(e["mods"]))


cm.mainloop()
