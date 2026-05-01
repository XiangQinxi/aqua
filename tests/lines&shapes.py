import charmy as cm


window = cm.Window(size=(300, 160))
window.title = "Lines & Shapes"

test_polyline = cm.shape.PolyLine([
    (10, 10), (50, 150), (200, 300), (30, 30)
    ])
test_arc = cm.shape.CircleArc((100, 100), 50, 0, 290)

test_polyline.draw(window, cm.texture.Color((255, 0, 0)))
test_arc.draw(window, cm.texture.Color((10, 10, 255)))


cm.mainloop()
