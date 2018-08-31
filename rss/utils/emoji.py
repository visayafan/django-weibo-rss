import logging
import os

import wget
from PIL import Image
from bs4 import BeautifulSoup

dir_to_store_image = '../static/images'

logging.basicConfig(level=logging.INFO)


def download_emoji():
    with open('weibo_emoji.html', encoding='utf-8') as file:
        filenames = []
        b = BeautifulSoup(file.read(), 'html.parser')
        lis_tag = b.find_all('li')
        if lis_tag:
            for li_tag in lis_tag:
                title = li_tag.get('title')
                url = 'http:' + li_tag.img.get('src')
                os.makedirs(dir_to_store_image, exist_ok=True)
                image_filename = url.split('/')[-1]
                wget.download(url, os.path.join(dir_to_store_image, image_filename))
                logging.info('Downloading ' + url)
                filenames.append(image_filename)
    return filenames


def shrink_emoji():
    for image_filename in os.listdir(dir_to_store_image):
        logging.info('Resizing ' + image_filename)
        image_filename_with_path = os.path.join(dir_to_store_image, image_filename)
        Image.open(image_filename_with_path).resize((20, 20)).save(image_filename_with_path)


emoji_names = ['2018newyear_richdog_thumb.gif', '2018new_aini_org.png', '2018new_aoteman_thumb.png', '2018new_baibai_thumb.png', '2018new_baobao_thumb.png', '2018new_beishang_org.png',
               '2018new_bingbujiandan_thumb.png', '2018new_bishi_thumb.png', '2018new_bizui_org.png', '2018new_caonima_thumb.png', '2018new_chanzui_thumb.png', '2018new_chigua_thumb.png',
               '2018new_chijing_org.png', '2018new_chongjing_org.png', '2018new_dahaqian_org.png', '2018new_dalian_org.png', '2018new_dangao_thumb.png', '2018new_ding_org.png',
               '2018new_doge02_org.png', '2018new_erha_org.png', '2018new_feiji_thumb.png', '2018new_feizao_thumb.png', '2018new_ganbei_org.png', '2018new_geili_thumb.png', '2018new_good_thumb.png',
               '2018new_guanggao_thumb.png', '2018new_gui_org.png', '2018new_guolai_thumb.png', '2018new_guzhang_thumb.png', '2018new_hahashoushi_org.png', '2018new_haha_thumb.png',
               '2018new_haixiu_org.png', '2018new_han_org.png', '2018new_heixian_thumb.png', '2018new_heng_thumb.png', '2018new_huaixiao_org.png', '2018new_huatong_thumb.png',
               '2018new_huaxin_org.png', '2018new_hufen02_org.png', '2018new_jiayou_thumb.png', '2018new_jiyan_org.png', '2018new_keai_org.png', '2018new_kelian_org.png', '2018new_kouzhao_thumb.png',
               '2018new_kulou_thumb.png', '2018new_kun_thumb.png', '2018new_kuxiao_thumb.png', '2018new_ku_org.png', '2018new_landelini_org.png', '2018new_lazhu_org.png', '2018new_leimu_org.png',
               '2018new_liwu_org.png', '2018new_lvsidai_thumb.png', '2018new_miaomiao_thumb.png', '2018new_nanhai_thumb.png', '2018new_ningwen_org.png', '2018new_no_org.png', '2018new_nu_thumb.png',
               '2018new_nvhai_thumb.png', '2018new_ok_org.png', '2018new_qian_thumb.png', '2018new_qinqin_thumb.png', '2018new_quantou_thumb.png', '2018new_ruo_thumb.png',
               '2018new_shachenbao_thumb.png', '2018new_shayan_org.png', '2018new_shengbing_thumb.png', '2018new_shiwang_thumb.png', '2018new_shuai_thumb.png', '2018new_shuijiao_thumb.png',
               '2018new_sikao_thumb.png', '2018new_taikaixin_org.png', '2018new_taiyang_org.png', '2018new_tanshou_org.png', '2018new_tianping_thumb.png', '2018new_touxiao_org.png',
               '2018new_tuzi_thumb.png', '2018new_tu_thumb.png', '2018new_wabi_thumb.png', '2018new_weibo_org.png', '2018new_weifeng_thumb.png', '2018new_weiguan_org.png', '2018new_weiqu_thumb.png',
               '2018new_weiwu_thumb.png', '2018new_weixioa02_org.png', '2018new_wenhao_thumb.png', '2018new_woshou_thumb.png', '2018new_wu_thumb.png', '2018new_xiangji_thumb.png',
               '2018new_xianhua_org.png', '2018new_xiaoerbuyu_org.png', '2018new_xiaoku_thumb.png', '2018new_xinlang_thumb.png', '2018new_xinsui_thumb.png', '2018new_xin_thumb.png',
               '2018new_xiongmao_thumb.png', '2018new_xixi_thumb.png', '2018new_xizi_thumb.png', '2018new_xu_org.png', '2018new_ye_thumb.png', '2018new_yinxian_org.png', '2018new_yinyue_org.png',
               '2018new_youhengheng_thumb.png', '2018new_yueliang_org.png', '2018new_yunduo_thumb.png', '2018new_yun_thumb.png', '2018new_yu_thumb.png', '2018new_zan_org.png',
               '2018new_zhongguozan_org.png', '2018new_zhong_org.png', '2018new_zhouma_thumb.png', '2018new_zhuakuang_org.png', '2018new_zhutou_thumb.png', '2018new_zuohengheng_thumb.png',
               '2018new_zuoyi_org.png', 'dorachijing_thumb.gif', 'dorahaipa_thumb.gif', 'dorahan_thumb.gif', 'dorahaose_thumb.gif', 'dora_kaixin_thumb.png', 'dora_meiwei_thumb.png',
               'dora_qinqin_thumb.png', 'dora_wunai_thumb.png', 'dora_xiao_thumb.png', 'eventtravel_thumb.gif', 'fulian3_dongbing01_thumb.png', 'fulian3_gangtiexia01_thumb.png',
               'fulian3_gelute01_thumb.png', 'fulian3_haoke01_thumb.png', 'fulian3_heiguafu01_thumb.png', 'fulian3_leishen01_thumb.png', 'fulian3_luoji01_thumb.png',
               'fulian3_meiguoduizhang01_thumb.png', 'fulian3_qiyiboshi01_thumb.png', 'fulian3_zhizhuxia01_thumb.png', 'hot_blankstar_thumb.png', 'hot_halfstar_thumb.png', 'hot_star171109_thumb.png',
               'jiqimaodaxiong_thumb.gif', 'jiqimaojingxiang_thumb.gif', 'jiqimaopanghu_thumb.gif', 'jiqimaoxiaofu_thumb.gif', 'jqmbwtxing_thumb.gif', 'jqmweixiao_thumb.gif', 'kandiev2_thumb.gif',
               'kanzhangv2_thumb.gif', 'lxhainio_thumb.gif', 'lxhlike_thumb.gif', 'lxhqiuguanzhu_thumb.gif', 'lxhtouxiao_thumb.gif', 'lxhwahaha_thumb.gif', 'lxhxiudada_thumb.gif', 'lxhzan_thumb.gif',
               'manwei_huangfengnv_thumb (1).png', 'manwei_huangfengnv_thumb.png', 'manwei_yiren_thumb (1).png', 'manwei_yiren_thumb.png', 'mickey_aini_thumb.png', 'mickey_aloha_thumb.png',
               'mickey_bixin_thumb.png', 'mickey_daku_thumb.png', 'mickey_feiwen_thumb.png', 'mickey_xihuan_thumb.png', 'qixi2018_chigouliang_thumb.png', 'qixi2018_xiaoxinxin_thumb.png',
               'remen_zuiyou180605_thumb.png', 'xhrnew_baiyan_org.png', 'xhrnew_buxie_org.png', 'xhrnew_deyi_thumb.png', 'xhrnew_gaoxing_org.png', 'xhrnew_huaixiao_thumb.png',
               'xhrnew_jiandaoshou_org.png', 'xhrnew_jingya_thumb.png', 'xhrnew_weiqu_org.png', 'xhrnew_weixiao_org.png', 'xhrnew_wunai_thumb.png']

if __name__ == '__main__':
    emoji_names = download_emoji()
    shrink_emoji()
    print(emoji_names)
