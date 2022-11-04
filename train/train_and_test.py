import torch.nn as nn
import torch


def train(model, device, train_loader, optimizer, epoch):
    model.train()  # 将模型设置为训练模式
    loss_func = nn.CrossEntropyLoss()
    for step, (x, y) in enumerate(train_loader):
        x, y = x.to(device), y.to(device)
        optimizer.zero_grad()
        y_ = model(x)
        loss = loss_func(y_, y)
        loss.backward()
        optimizer.step()  # 这一步一定要有，用于更新参数，之前由于漏写了括号导致参数没有更新，排BUG排了半天

        if (step + 1) % 10 == 0:
            print('Train Epoch:{} [{}/{} ({:.0f}%)]\tLoss:{:.6f}'.format(
                epoch, step * len(x), len(train_loader.dataset),
                       100. * step / len(train_loader), loss.item()
            ))


def test(model, device, test_loader):
    model.eval()
    loss_func = nn.CrossEntropyLoss(reduction='sum')
    test_loss = 0.0
    acc = 0
    for step, (x, y) in enumerate(test_loader):
        x, y = x.to(device), y.to(device)
        with torch.no_grad():
            y_ = model(x)
        test_loss += loss_func(y_, y)
        pred = y_.max(-1, keepdim=True)[1]
        acc += pred.eq(y.view_as(pred)).sum().item()
    test_loss /= len(test_loader.dataset)
    print('\nTest set:Average loss:{:.4f},Accuracy:{}/{} ({:.0f}%)'.format(
        test_loss, acc, len(test_loader.dataset),
        100 * acc / len(test_loader.dataset)
    ))

    return acc / len(test_loader.dataset)
