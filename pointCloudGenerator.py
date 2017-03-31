import numpy as np
import cv2
from common import constantSource as cs

ply_header = '''ply
format ascii 1.0
element vertex %(vert_num)d
property float x
property float y
property float z
property uchar red
property uchar green
property uchar blue
end_header
'''

def write_ply(fn, verts, colors):
    verts = verts.reshape(-1, 3)
    colors = colors.reshape(-1, 3)
    verts = np.hstack([verts, colors])
    with open(fn, 'wb') as f:
        f.write((ply_header % dict(vert_num=len(verts))).encode('utf-8'))
        np.savetxt(f, verts, fmt='%f %f %f %d %d %d ')

def generatePointCloud(disp, imgs, Q=None, matFile=None):
    minDisp, maxDisp = cs.getDisparityValue()
    numDisp = maxDisp - minDisp

    img = imgs[0] # Here img corresponds to left image

    print('Generating 3d Point Cloud...')
    h, w = img.shape[:2]
    if Q is None:
        f = 0.8*w # guess for focal length
        Q = np.float32([[1, 0, 0, -0.5*w],
                        [0, -1, 0, 0.5*h], # turn points 180 deg around x-axis,
                        [0, 0, 0, -f], # so that y-axis looks up
                        [0, 0, 1, 0]])

    points = cv2.reprojectImageTo3D(disp, Q)
    # TODO: img is black n white
    colors = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    mask = disp > disp.min()
    out_points = points[mask]
    out_colors = colors[mask]

    # TODO: insert code to append to a global 3D point cloud container variable
    fileName = "pointCloud.ply"
    write_ply(fileName, out_points, out_colors)
    print('%s saved' % 'out.ply')

    cv2.imshow("left", img)
    cv2.imshow("disparity", (disp-minDisp)/numDisp)
    cv2.waitKey()
    cv2.destroyAllWindows()
