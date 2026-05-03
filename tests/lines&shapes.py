import charmy as cm
from charmy.this import THE_POEM as charmy_bible # For later text rendering test (maybe)


window = cm.Window(size=(540, 480))
window.title = "Lines & Shapes"

test_polyline = cm.shape.PolyLine([
    (500, 10), (50, 150), (200, 300), (70, 30)
    ])
test_arc = cm.shape.CircleArc((100, 100), 50, 0, 290)
test_quadratic_bezier = cm.shape.QuadraticBezier([
    (150, 200), (300, 300), (10, 400)
    ])

test_polyline.draw(window, (255, 100, 100))
test_arc.draw(window, (100, 100, 255))
test_quadratic_bezier.draw(window, (100, 255, 100, 100), width=2)


cm.mainloop()