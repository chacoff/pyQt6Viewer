import numpy as np
import matplotlib.pyplot as plt

img = np.array([[21.0, 20.0, 22.0, 24.0, 18.0, 11.0, 23.0],
                [21.0, 20.0, 22.0, 99.0, 18.0, 11.0, 23.0],
                [21.0, 20.0, 22.0, 99.0, 18.0, 11.0, 23.0],
                [21.0, 20.0, 22.0, 99.0, 18.0, 11.0, 23.0],
                [21.0, 20.0, 22.0, 99.0, 18.0, 11.0, 23.0],
                [21.0, 20.0, 22.0, 99.0, 18.0, 11.0, 23.0],
                [21.0, 20.0, 22.0, 24.0, 18.0, 11.0, 23.0]])


# compute gradient of image
gx, gy = np.gradient(img)


# plotting
plt.close("all")
plt.figure()
plt.suptitle("Image, and it gradient along each axis")
ax = plt.subplot(131)
ax.axis("off")
ax.imshow(img)
ax.set_title("image")

ax = plt.subplot(132)
ax.axis("off")
ax.imshow(gx)
ax.set_title("gx")

ax = plt.subplot(133)
ax.axis("off")
ax.imshow(gy)
ax.set_title("gy")
plt.show()