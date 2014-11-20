import numpy as np
import matplotlib.pyplot as plt


def draw_ellipse(x, y, cov):
    #from https://github.com/joferkington/oost_paper_code/blob/master/error_ellipse.py
    from matplotlib.patches import Ellipse
    def eigsorted(cov):
        vals, vecs = np.linalg.eigh(cov)
        order = vals.argsort()[::-1]
        return vals[order], vecs[:, order]

    ax = plt.gca()

    vals, vecs = eigsorted(cov)
    theta = np.degrees(np.arctan2(*vecs[:, 0][::-1]))

    # Width and height are "full" widths, not radius
    width, height = 2 * 2 * np.sqrt(vals)
    ellip = Ellipse(xy=[x, y], width=width, height=height, angle=theta, fill=False)
    ax.add_artist(ellip)