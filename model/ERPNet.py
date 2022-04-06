import torch
import torch.nn as nn
from torchvision import models

from .resnet_model import *

def change(x):
    x1 = torch.where(x == 1, torch.full_like(x, 1-(1e-5)), x)
    x2 = torch.where(x1 == 0, torch.full_like(x1, (1e-5)), x1)

    return x2

class ERPNet(nn.Module):
    def __init__(self):
        super(ERPNet,self).__init__()
        resnet = models.resnet34(pretrained=True)
        #-------------Encoder--------------#
        #stage 1
        self.encoder1 = nn.Sequential(
            nn.Conv2d(3,64,3,padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            resnet.layer1
        ) # 224
        #stage 2
        self.encoder2 = resnet.layer2 # 112
        #stage 3
        self.encoder3 = resnet.layer3 # 56
        #stage 4
        self.encoder4 = resnet.layer4 # 28
        #stage 5
        self.encoder5 = nn.Sequential(
            nn.MaxPool2d(2,2,ceil_mode=True),
            BasicBlock(512,512),
            BasicBlock(512,512),
            BasicBlock(512,512)
        ) # 14
        #-------------Upsampling--------------#
        self.upscore2 = nn.Upsample(scale_factor=2, mode='bilinear',align_corners=True)
        self.upscore4 = nn.Upsample(scale_factor=4, mode='bilinear',align_corners=True)
        self.upscore8 = nn.Upsample(scale_factor=8, mode='bilinear',align_corners=True)
        self.upscore16 = nn.Upsample(scale_factor=16, mode='bilinear',align_corners=True)
        #-------------Poolling--------------#
        self.pool2 = nn.MaxPool2d(2,2,ceil_mode=True)
        self.pool4 = nn.MaxPool2d(4,4,ceil_mode=True)
        self.pool8 = nn.MaxPool2d(8,8,ceil_mode=True)
        self.pool16 = nn.MaxPool2d(16,16,ceil_mode=True)
        #-------------Decoder Label--------------#
        #stage 5
        self.decoder_l5 = nn.Sequential(
            nn.Conv2d(512,512,3,dilation=2, padding=2),
            nn.BatchNorm2d(512),
            nn.ReLU(inplace=True),
            nn.Conv2d(512,512,3,padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU(inplace=True),
            nn.Conv2d(512,512,3,padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU(inplace=True)
        )
        #stage 4
        self.decoder_l4 = nn.Sequential(
            nn.Conv2d(512+512+1,512,3,dilation=2, padding=2),
            nn.BatchNorm2d(512),
            nn.ReLU(inplace=True),
            nn.Conv2d(512,512,3,padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU(inplace=True),
            nn.Conv2d(512,256,3,padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True)
        )
        #stage3
        self.decoder_l3 = nn.Sequential(
            nn.Conv2d(256+256+1,256,3,dilation=2, padding=2),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.Conv2d(256,256,3,padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.Conv2d(256,128,3,padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True)
        )
        #stage2
        self.decoder_l2 = nn.Sequential(
            nn.Conv2d(128+128+1,128,3,dilation=2, padding=2),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.Conv2d(128,128,3,padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.Conv2d(128,64,3,padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True)
        )
        #stage1
        self.decoder_l1 = nn.Sequential(
            nn.Conv2d(64+64+1,64,3,dilation=2, padding=2),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.Conv2d(64,64,3,padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.Conv2d(64,64,3,padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True)
        )
        #-------------Decoder Edge--------------#
        #stage 5
        self.decoder_e5 = nn.Sequential(
            nn.Conv2d(512,512,3,dilation=2, padding=2),
            nn.BatchNorm2d(512),
            nn.ReLU(inplace=True),
            nn.Conv2d(512,512,3,padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU(inplace=True),
            nn.Conv2d(512,512,3,padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU(inplace=True)
        )
        #stage 4
        self.decoder_e4 = nn.Sequential(
            nn.Conv2d(512+512+512,512,3,dilation=2, padding=2),
            nn.BatchNorm2d(512),
            nn.ReLU(inplace=True),
            nn.Conv2d(512,512,3,padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU(inplace=True),
            nn.Conv2d(512,256,3,padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True)
        )
        #stage 3
        self.decoder_e3 = nn.Sequential(
            nn.Conv2d(256+512+256,256,3,dilation=2, padding=2),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.Conv2d(256,256,3,padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.Conv2d(256,128,3,padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True)
        )
        #stage 2
        self.decoder_e2 = nn.Sequential(
            nn.Conv2d(128+256+128,128,3,dilation=2, padding=2),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.Conv2d(128,128,3,padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.Conv2d(128,64,3,padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True)
        )
        #stage 1
        self.decoder_e1 = nn.Sequential(
            nn.Conv2d(64+128+64,64,3,dilation=2, padding=2),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.Conv2d(64,64,3,padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.Conv2d(64,64,3,padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True)
        )
        #-------------Side output--------------#
        ## Edge
        self.conv_oute5 = nn.Conv2d(512,1,3,padding=1)
        self.conv_oute4 = nn.Conv2d(256,1,3,padding=1)
        self.conv_oute3 = nn.Conv2d(128,1,3,padding=1)
        self.conv_oute2 = nn.Conv2d(64,1,3,padding=1)
        self.conv_oute1 = nn.Conv2d(64,1,3,padding=1)
        ## Sal
        self.conv_out = nn.Conv2d(5,1,3,padding=1)
        #-------------EPAU--------------#
        self.conv_epau5 = nn.Sequential(
            nn.Conv2d(512,256,3,padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.Conv2d(256,256,1,padding=0),
            nn.Conv2d(256,1,3,padding=1),
            nn.Sigmoid()
        )
        self.conv_epau4 = nn.Sequential(
            nn.Conv2d(256,128,3,padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.Conv2d(128,128,1,padding=0),
            nn.Conv2d(128,1,3,padding=1),
            nn.Sigmoid()
        )
        self.conv_epau3 = nn.Sequential(
            nn.Conv2d(128,64,3,padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.Conv2d(64,64,1,padding=0),
            nn.Conv2d(64,1,3,padding=1),
            nn.Sigmoid()
        )
        self.conv_epau2 = nn.Sequential(
            nn.Conv2d(64,32,3,padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.Conv2d(32,32,1,padding=0),
            nn.Conv2d(32,1,3,padding=1),
            nn.Sigmoid()
        )
        self.conv_epau1 = nn.Sequential(
            nn.Conv2d(64,32,3,padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.Conv2d(32,32,1,padding=0),
            nn.Conv2d(32,1,3,padding=1),
            nn.Sigmoid()
        )

    def forward(self,x):
        #-------------Encoder--------------#
        score1 = self.encoder1(x)
        score2 = self.encoder2(score1)
        score3 = self.encoder3(score2)
        score4 = self.encoder4(score3)
        score5 = self.encoder5(score4)
        #-------------Decoder Edge--------------#
        #stage 5
        scoree5 = self.decoder_e5(score5)
        t = torch.cat((scoree5,score5),1)
        t = self.upscore2(t)

        #stage 4
        scoree4 = self.decoder_e4(torch.cat((t,score4),1))
        t = torch.cat((scoree4,score4),1)
        t = self.upscore2(t)

        #stage 3
        scoree3 = self.decoder_e3(torch.cat((t,score3),1))
        t = torch.cat((scoree3,score3),1)
        t = self.upscore2(t)

        #stage 2
        scoree2 = self.decoder_e2(torch.cat((t,score2),1))
        t = torch.cat((scoree2,score2),1)
        t = self.upscore2(t)

        #stage 1
        scoree1 = self.decoder_e1(torch.cat((t,score1),1))
        #-------------Side output--------------#
        oute5 = self.conv_oute5(scoree5)
        oute5 = self.upscore16(oute5)
        oute5 = torch.sigmoid(oute5)

        oute4 = self.conv_oute4(scoree4)
        oute4 = self.upscore8(oute4)
        oute4 = torch.sigmoid(oute4)

        oute3 = self.conv_oute3(scoree3)
        oute3 = self.upscore4(oute3)
        oute3 = torch.sigmoid(oute3)

        oute2 = self.conv_oute2(scoree2)
        oute2 = self.upscore2(oute2)
        oute2 = torch.sigmoid(oute2)
        
        oute1 = self.conv_oute1(scoree1)
        oute1 = torch.sigmoid(oute1) # turn to 0-1
        #-------------Copy SE to different channels--------------#
        SE = torch.cat((oute1,oute1),1) #2 Channels
        SE = torch.cat((SE,SE),1) #4 Channels
        SE = torch.cat((SE,SE),1) #8 Channels
        SE = torch.cat((SE,SE),1) #16 Channels
        SE = torch.cat((SE,SE),1) #32 Channels
        SE_64 = torch.cat((SE,SE),1) #64 Channels
        SE_128 = torch.cat((SE_64,SE_64),1) #128 Channels
        SE_256 = torch.cat((SE_128,SE_128),1) #256 Channels
        SE_512 = torch.cat((SE_256,SE_256),1) #512 Channels
        #-------------Decoder Label--------------#
        #stage 5
        scorel5 = self.decoder_l5(score5)
        ##EPAU
        SE_down5 = self.pool16(SE_512)
        OE_5 = torch.mul(SE_down5,scorel5) + scorel5
        PA5 = self.conv_epau5(OE_5)
        t = torch.cat((scorel5, PA5),1)
        t = self.upscore2(t)

        #stage 4
        scorel4= self.decoder_l4(torch.cat((t,score4),1))
        ##EPAU
        SE_down4 = self.pool8(SE_256)
        OE_4 = torch.mul(SE_down4,scorel4) + scorel4
        PA4 = self.conv_epau4(OE_4)
        t = torch.cat((scorel4, PA4),1)
        t = self.upscore2(t)

        #stage 3
        scorel3 = self.decoder_l3(torch.cat((t,score3),1))
        ##EPAU
        SE_down3 = self.pool4(SE_128)
        OE_3 = torch.mul(SE_down3,scorel3) + scorel3
        PA3 = self.conv_epau3(OE_3)
        t = torch.cat((scorel3, PA3),1)
        t = self.upscore2(t)

        #stage 2
        scorel2 = self.decoder_l2(torch.cat((t,score2),1))
        ##EPAU
        SE_down2 = self.pool2(SE_64)
        OE_2 = torch.mul(SE_down2,scorel2) + scorel2
        PA2 = self.conv_epau2(OE_2)
        t = torch.cat((scorel2, PA2),1)
        t = self.upscore2(t)

        #stage 1
        scorel1 = self.decoder_l1(torch.cat((t,score1),1))
        ##EPAU
        OE_1 = torch.mul(SE_64,scorel1) + scorel1
        PA1 = self.conv_epau1(OE_1)
        #-------------Side Output--------------#
        outl1 = PA1
        outl2 = self.upscore2(PA2)
        outl3 = self.upscore4(PA3)
        outl4 = self.upscore8(PA4)
        outl5 = self.upscore16(PA5)
        out = torch.cat((outl1,outl2,outl3,outl4,outl5),1)
        out = self.conv_out(out)
        out = torch.sigmoid(out)
        #-------------Final output--------------#
        return change(out), change(outl1), change(outl2), change(outl3), change(outl4), change(outl5), \
            change(oute1), change(oute2), change(oute3), change(oute4), change(oute5)