import LWIRImageTool as lit
import numpy as np
import matplotlib.pyplot as plt


image_config = lit.ImageDataConfig(filename = "/home/cjw9009/Desktop/suas_data/MTF Test/20260317_101021_872_LWIR_R.jpg", filetype="rjpeg")
Factory = lit.ImageDataFactory()
image = Factory.create_from_file(image_config)
plt.imshow(image.raw_counts, cmap="gray")
plt.show()

lsf = image.raw_counts[265,304:330]
plt.plot(lsf)
plt.show()