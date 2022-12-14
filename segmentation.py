from torchvision.models.detection import maskrcnn_resnet50_fpn, MaskRCNN_ResNet50_FPN_Weights
import torch
import matplotlib.pyplot as plt
import torchvision.transforms.functional as F
import numpy as np
from torchvision.utils import draw_segmentation_masks
from itertools import repeat
class ImageSegmentation( object ):

    def __init__(self) -> None:
        pass

    @staticmethod
    def showImages( imgs ):
        if not isinstance( imgs, list ):
            imgs = list( imgs )
        fig, axs = plt.subplots(ncols=len( imgs ), squeeze=False)
        for i, img in enumerate(imgs):
            img = img.detach()
            img = F.to_pil_image(img)
            axs[0, i].imshow( np.asarray( img ) )
            axs[0, i].set( xticklabels=[], yticklabels=[], xticks=[], yticks=[] )

    @staticmethod
    def performImageSegmentationInternal( rgb_image:np.ndarray, resnet_image:np.ndarray, segmentation_threshold:float, alpha:float, counter:int ):
        print("Running performImageSegmentationInternal", counter)
        masked_img = draw_segmentation_masks( rgb_image[counter], ( resnet_image[counter]['masks'] > segmentation_threshold )[0][0], alpha=alpha )
        masked_img = masked_img.numpy().transpose( 1, 2, 0 )
        return masked_img

    @staticmethod
    def performImageSegmentation( pool, rgb_img_list:list, segmentation_threshold:float, alpha:float ) -> tuple:

        weights = MaskRCNN_ResNet50_FPN_Weights.DEFAULT
        transforms = weights.transforms()

        images = [ transforms(d) for d in rgb_img_list ]
        print("transfoemed images")

        with torch.no_grad():
            model = maskrcnn_resnet50_fpn(weights=weights, progress=False)
            model = model.eval()

            output = model(images)
        
        print("model created")

        masked_images = pool.starmap(
            ImageSegmentation.performImageSegmentationInternal, 
            zip(
                repeat(rgb_img_list), 
                repeat(output), 
                repeat(segmentation_threshold),
                repeat(alpha),
                range(len(rgb_img_list))
            )
        )

        print("passed to pool")

        img_output = output[-1]

        print([weights.meta["categories"][label] for label in img_output['labels'][img_output['scores'] > segmentation_threshold]])

        # masks_thresh = img_output['masks'][img_output['scores'] > segmentation_threshold ]

        # ImageSegmentation.showImages( [ masks_thresh[i,0,:,:] for i in range( masks_thresh.shape[0] ) ] )

        # masked_img = draw_segmentation_masks( rgb_img_list[-1], ( img_output['masks'] > segmentation_threshold )[0][0], alpha=alpha )

        # ImageSegmentation.showImages( masked_img )

        # masked_img = masked_img.numpy().transpose( 1, 2, 0 )
        # masked_img = masked_img[:, :, [ 2, 1, 0 ] ]

        return ( output, masked_images )