# pylint: skip-file
import numpy as np
import mxnet as mx
import os
from PIL import Image

pallete = [ 0,0,0,
            255,255,255 ]
model_previx = "model_pascal/FCN8s_VGG16"
epoch = 2
ctx = mx.gpu(0)

def get_imgpath():
    cwd = os.getcwd()
    file_names = os.listdir('test2')
    for file_name in file_names:
        yield os.path.join(cwd, 'test2', file_name)

def get_data(img_path):
    """get the (1, 3, h, w) np.array data for the img_path"""
    mean = np.array([123.68, 116.779, 103.939])  # (R,G,B)
    img = Image.open(img_path)
    img = np.array(img, dtype=np.float32)
    reshaped_mean = mean.reshape(1, 1, 3)
    img = img - reshaped_mean
    img = np.swapaxes(img, 0, 2)
    img = np.swapaxes(img, 1, 2)
    img = np.expand_dims(img, axis=0)
    return img

def main():
    fcnxs, fcnxs_args, fcnxs_auxs = mx.model.load_checkpoint(model_previx, epoch)
    for img in get_imgpath():
        seg = img.replace("jpg", "png")
        seg = seg.replace("test2", "test2_mask")
        print seg
        fcnxs_args["data"] = mx.nd.array(get_data(img), ctx)
        data_shape = fcnxs_args["data"].shape
        print data_shape
        label_shape = (1, data_shape[2]*data_shape[3])
        fcnxs_args["softmax_label"] = mx.nd.empty(label_shape, ctx)
        exector = fcnxs.bind(ctx, fcnxs_args ,args_grad=None, grad_req="null", aux_states=fcnxs_args)
        exector.forward(is_train=False)
        output = exector.outputs[0]
        out_img = np.uint8(np.squeeze(output.asnumpy().argmax(axis=1)))
        out_img = Image.fromarray(out_img)
        out_img.putpalette(pallete)
        out_img.save(seg)

if __name__ == "__main__":
    main()
