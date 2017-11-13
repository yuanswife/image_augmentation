## image_augmentation
lung-nodule-detection : cube image augmentation.

在现实条件下，medical image的数据量一般都不足，此时利用数据增广来扩充数据集就显得尤为重要。

####背景
我们将每个病人的CT scan（3D）切成一个个cube。\n
已知肺结节的坐标从而可得到每个cube对应的标签（positive or negtive）。\n
将已知标签的cube输入网络训练得到模型。\n
对于需要预测的CT scan，相当于用一个3D窗口（与cube同一个size）在CT scan上一步步滑动，预测每个3D窗口的nodule_chance。我们可以根据步数、步长、滑动窗口(cube)的大小来算出每个滑动窗口的坐标，从而获得结节(nodule_chance > threshold)的坐标。

从上面可知，网络的输入是cube image（如：z轴大小为64的cube被平铺在一张2D image上，即变成8x8阵列，见test_aug_image）。
所以我们是针对cube image做数据增广。需要用到两个操作：
1、加载cube image(load_cube_image());
2、将cube image还原成一张张image，对每张image做相同的增广操作，然后再存储为新的cube image(save_aug_cube_image())。
