import os
from torch.utils.data import Dataset
from torchvision import transforms
from PIL import Image
from torch.utils.data import DataLoader

def make_dataset(root):
    items = []
    pred_list = os.path.join(root, 'preds')
    gt_list = os.path.join(root, 'gts')

    preds = os.listdir(pred_list)
    gts = os.listdir(gt_list)

    preds.sort()
    gts.sort()

    for pred, gt in zip(preds, gts):
        item = (os.path.join(pred_list, pred),
                os.path.join(gt_list, gt))
        items.append(item)
    return items


class MedicalImageDataset(Dataset):

    def __init__(self, root_dir, transform=transforms.ToTensor()):
        self.root_dir = root_dir
        self.imgs = make_dataset(root_dir)
        self.transform = transform

    def __len__(self):
        return len(self.imgs)

    def __getitem__(self, index):
        pred_path, gt_path = self.imgs[index]
        pred = Image.open(pred_path).convert('RGB')
        gt = Image.open(gt_path).convert('RGB')
        # img = Image.open(img_path).convert('L')
        # mask = Image.open(mask_path).convert('L')
        pred = self.transform(pred)
        gt = self.transform(gt)

        return [pred, gt, pred_path, gt_path]


datasets = MedicalImageDataset(r'D:\datasets\hi')
train_loader = DataLoader(datasets,
                          batch_size=1,
                          num_workers=0,
                          shuffle=True)

for index, data in enumerate(train_loader):
    pred, gt, path, path2 = data
    print(path[0], '\n', path2[0])
