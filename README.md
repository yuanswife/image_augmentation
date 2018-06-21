## image_augmentation
lung-nodule-detection : cube image augmentation.

在现实条件下，medical image的数据量一般都不足，此时利用数据增广来扩充数据集就显得尤为重要。

#### 背景 <br>
我们将每个病人的CT scan（3D）切成一个个cube。 <br>
已知肺结节的坐标从而可得到每个cube对应的标签（positive or negtive），将已知标签的cube输入网络训练得到模型。 <br>
对于需要预测的CT scan，相当于用一个3D窗口（与cube同一个size）在CT scan上一步步滑动，预测每个3D窗口的nodule_chance。我们可以根据步数、步长、滑动窗口(cube)的大小来算出每个滑动窗口的坐标，从而获得结节(nodule_chance > threshold)的坐标。 

从上面可知，网络的输入是cube image（如：将64x64x64的cube平铺在一张2D image上，即变成含有8x8=64张64x64 2D image的阵列，见test_aug_image）。 <br>
所以我们是针对cube image做数据增广。需要用到两个操作： <br>
1、加载cube image(load_cube_image()); <br>
2、将cube image还原成一张张image(64x64)，对每张image做相同的增广操作，然后再存储为新的cube image(save_aug_cube_image())。

#### 运行<br>
- 对cube image还原后的一张张image进行操作：<br>
左右翻转：python imgaug.py <img_dir> <dst_img_dir> fliph <br>
上下翻转：python imgaug.py <img_dir> <dst_img_dir> flipv <br>
旋转：python imgaug.py <img_dir> <dst_img_dir> rot_50 rot_90 rot_180 rot_-90 <br>
平移translate：python imgaug.py <img_dir> <dst_img_dir> trans_5_5 trans_10_10<br>
【不规则缩放：python imgaug.py <img_dir> <dst_img_dir> zoom_0_50_300_150】<br> 

- 对full cube image(平铺的cube image)进行操作：<br>
模糊：python imgaug_fullimg.py <img_dir> <dst_img_dir> blur_1.0 blur_1.5 <br>
噪音：python imgaug_fullimg.py <img_dir> <dst_img_dir> noise_0.005 noise_0.01 <br>
