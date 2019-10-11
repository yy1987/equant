import os
import sys
import datetime
import shutil
import requests
import zipfile
import traceback
import configparser
import signal, psutil

VERSION = ""
EPVERSION = ""
EQVERURL = "https://gitee.com/epolestar/equant/raw/master/VerNo.txt"
EPVERURl = "https://gitee.com/epolestar/equant/raw/master/EpVerNo.txt"
equantUrl    = "https://epolestar-master-1255628687.cos.ap-beijing.myqcloud.com/"
epolestarUrl = "https://epolestar95-1255628687.cos.ap-beijing.myqcloud.com/epolestar.zip"

urls         = [equantUrl, epolestarUrl]
tags         = ["equant", "epolestar"]
EPOURLTAG    = [epolestarUrl, "epolestar"]
EQUURLTAG    = [equantUrl, "equant"]
zipname      = ["equant.zip", "epolestar.zip"]


# 脚本所在路径
dirPath = os.getcwd()

# 工作路径(appdata所在路径)
# appPath = os.getenv("APPDATA")
if not os.path.exists(os.path.abspath(os.path.join(dirPath, "..\\equant_backups"))):
    os.makedirs(os.path.join(dirPath, "..\\equant_backups"))
os.chdir(os.path.abspath(os.path.join(dirPath, "..\\equant_backups")))

workDir = os.getcwd()

styPath = os.path.join(workDir, "equant-master\\src\\strategy")
cfgPath = os.path.join(workDir, "equant-master\\src\\config")
logPath = os.path.join(workDir, "equant-master\\src\\log")

tempPath1 = os.path.join(dirPath, "src\\strategy")
tempPath2 = os.path.join(dirPath, "src\\config")
tempPath3 = os.path.join(dirPath, "src\\log")


# 备份用户文件
def backup(directory, des):
    if os.path.exists(directory):
        # ret = os.system(f'xcopy "{directory}" "{des}" /y /e /i /h')
        ret = os.system(
            f'xcopy "{directory}" "{des}" /y /e /i /h /exclude:..\\equant\\exclude.txt')
        if ret == 0:
            print("%s 备份成功！" % directory)
        return 1
    else:
        print("Equant or Equant-master directory dosen't exist!")
        return 0


# 关9.5
def killEpProcess():
    if "epolestar v9.5.exe" in os.popen('tasklist /fi "IMAGENAME eq %s"' % "epolestar v9.5.exe").read():
        # os.system("taskkill /f /im %s" % "epolestar v9.5.exe")
        os.system('taskkill /f /fi "IMAGENAME eq %s"' % "epolestar v9.5.exe")


# 杀进程及子进程
def killProcesses(parent_pid, sig=signal.SIGTERM):
    try:
        parent = psutil.Process(parent_pid)
    except psutil.NoSuchProcess:
        return
    children = parent.children(recursive=True)
    for process in children:
        process.send_signal(sig)
    try:
        os.system('taskkill /f /PID %d /fi "IMAGENAME eq python.exe"' % parent_pid)
    except:
        print("process %s doesn't exist" % parent_pid)


def requestZip(zipUrl, tag):
    """下载"""
    try:
        response = requests.get(zipUrl, timeout=5)
        response.raise_for_status()
        with open (tag+".zip", "wb") as f:
            f.write(response.content)
        print("%s download successfully!"%tag)
        return 1
    except Exception as e:
        print(tag, ":", "There is an exception %s when downloading file!" % (e))
        return 0


def zipFile(filename):
    """解压"""
    if not zipfile.is_zipfile(filename):
        print("%s is not an .zip file" % filename)
        return

    z = zipfile.ZipFile(filename)
    z.extractall()
    print("%s unzip successfully!" % filename)
    z.close()


def delzip(filename):
    """删除"""
    if os.path.exists(filename):
        os.remove(filename)
        print("Delete %s successfully!" % filename)


def delFile(path):
    if os.path.exists(path):
        print('%s存在先删除' % path)
        shutil.rmtree(path, onerror=readonly_handler)
        return 1
    return 0


# 移动文件
def mergeFile(src, dst):
    """

    :param src: 源路径
    :param dst: 目标路径
    :return:
    """
    if not os.path.exists(src):
        return

    if not os.path.exists(dst):
        os.makedirs(dst)

    for sf in os.listdir(src):

        sfPath = os.path.join(src, sf)
        dfPath = os.path.join(dst, sf)

        if os.path.isdir(sfPath):
            if os.path.basename(sfPath) == "__pycache__":
                continue

            if os.path.exists(dfPath):
                mergeFile(sfPath, dfPath)
            else:
                #print("Copy %s ===> %s"%(sfPath, dfPath))
                #shutil.copyfile(sfPath, dfPath)
                os.system(f'xcopy "{sfPath}" "{dfPath}" /y /e /i /h ')
        elif os.path.isfile(sfPath):
            if os.path.exists(dfPath):
                # shutil.copyfile(sfPath, dfPath)
                os.system(f'xcopy "{sfPath}" "{dfPath}" /y /e /i /h')
                #print("Cover %s ===> %s" % (sfPath, dfPath))
            else:
                # shutil.copy2(sfPath, dfPath)
                shutil.copy(sfPath, dfPath)
                #os.system(f"xcopy {sfPath} {dfPath} /y /e /i /h")
                #print("copy %s ===> %s" % (sfPath, dfPath))

def readonly_handler(func, path, ececinfo):
    os.chmod(path, 128)
    func(path)


# 检查equant是否需要更新
def checkEquUpdate():
    global VERSION
    try:
        if os.path.exists('../equant/VerNo.txt'):
            with open('../equant/VerNo.txt', 'r') as f:
                VERSION = f.read()
        
            lvl = VERSION.split('.')[:-1]
            lmv = '.'.join(lvl)
        
        rsp = requests.get(EQVERURL, timeout=10)
        if rsp.status_code == 200:
            rvstr = rsp.content.decode('utf-8')
            rvl = rvstr.split('.')[:-1]
            rmv = '.'.join(rvl)
            
        print("Start epolestar, version info, equant local version: %s, remote version: %s!" %(VERSION, rvstr))
            
        if (len(lmv) == len(rmv) > 0 and rmv > lmv) or ( 0 < len(lmv) != len(rmv)):
            return rmv

        else:
            print("Version don't need update, local:%s, remote:%s" %(lmv, rmv))
            return ""
    except Exception as e:
       print("checkUpdate epolestar Error:%s" %(traceback.format_exc()))


# 检查epolestar是否需要更新
def checkEpoUpdate():
    global EPVERSION
    try:
        if os.path.exists('../epolestar/update.ini'):
            conf_reader = configparser.ConfigParser()
            conf_reader.read('../epolestar/update.ini')
            EPVERSION = conf_reader.get("version", "cur")

            lmv = EPVERSION
        
        rsp = requests.get(EPVERURl, timeout=10)
        if rsp.status_code == 200:
            rvstr = rsp.content.decode('utf-8')
            with open('EPOVERSION.txt', 'w') as f:
                f.write(rvstr)

            if os.path.exists('EPOVERSION.txt'):
                conf_reader = configparser.ConfigParser()
                conf_reader.read('EPOVERSION.txt')
                ver = conf_reader.get("version", "cur")
            rmv = ver
            
        print("Start epolestar, version info, epolestar local version: %s, remote version: %s!" %(EPVERSION, rmv))
            
        if (len(lmv) == len(rmv) > 0 and rmv > lmv) or ( 0 < len(lmv) != len(rmv)):
            return rmv

        else:
            print("Epolestar version don't need update, local:%s, remote:%s" %(lmv, rmv))
            return ""
    except Exception as e:
       print("checkUpdate epolestar Error:%s" %(traceback.format_exc()))


def main(versionNo=None):
    inp = input(f"存在新版本{versionNo}可以升级,\n"
                "升级前请关闭极星9.5客户端和量化终端，否则将更新失败\n"
                "更新会覆盖本地代码，请做好备份。确认是否升级(y/n): ")
    if inp == 'y' or inp == 'Y':  # 确认升级
        # ======================更新epolestar和equant=============================
        chkEquRlt = checkEquUpdate()
        if chkEquRlt:
            EQUURLTAG[0] = EQUURLTAG[0] + chkEquRlt + ".0" + ".zip"
            reqRlt = requestZip(EQUURLTAG[0], EQUURLTAG[1])
            if reqRlt == 0:   # 下载失败
                 print("Equant下载过程出错，请重新尝试！")
                 return
        
        chkEpoRlt = checkEpoUpdate()
        if chkEpoRlt:
            reqRlt = requestZip(EPOURLTAG[0], EPOURLTAG[1])
            if reqRlt == 0:   # 下载失败
                 print("Epolestar下载过程出错，请重新尝试！")
                 return

        if not any([chkEquRlt, chkEpoRlt]):
            return

        # ===========================解压并删除压缩包=================================
        for name in zipname:
            zipFile(name)
            delzip(name)

        # ==========================关进程============================================
        killEpProcess()
        with open("..\\equant\\src\\log\\mainpid.log", "r") as f:
            pid = f.readline()
            if pid:
                killProcesses(int(pid))

        # ===========================备份文件==========================================
        time_now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")[:-3]
        if chkEquRlt:  # 备份equant
            directory, dest = dirPath, os.path.join(workDir, "equant_back"+time_now)
            equbacRlt = backup(directory, dest)
            if equbacRlt == 0:  # 路径不存在
                print("equant备份数据过程出错！")
                return
        if chkEpoRlt:
            directory = os.path.abspath(os.path.join(dirPath, "..\\epolestar"))
            dest = os.path.join(workDir, "epolestar_back_"+time_now)
            epobacRlt = backup(directory, dest)
            if epobacRlt == 0:  # 路径不存在
                print("equant备份数据过程出错！")
                return

        # ===========删除equant的代码部分，保留config, strategy, log文件夹，复制新版本=====================
        if chkEquRlt and equbacRlt:
            for file in os.listdir(os.path.join(dirPath, "src")):
                if file not in ["config", "log", "strategy"]:
                    path = os.path.join(dirPath, "src\\%s" % file)
                    if os.path.isdir(path):
                        delRet = delFile(path)
                        if delRet == 0:
                            print("%s 文件删除失败！" % path)
                            return
                    if os.path.isfile(path):
                        os.remove(path)

            # 合并config, strategy, log去重
            # TODO：会不会存在合并出错情况
            for src, dst in zip([styPath, cfgPath, logPath],
                                [tempPath1, tempPath2, tempPath3]):
                mergeFile(src, dst)

            # 将最新的代码拷贝到原目录中
            for file in os.listdir(os.path.join(workDir, "equant-master")):
                if file not in ["config", "log", "strategy"]:
                    spath = os.path.join(workDir, "equant-master\\%s" % file)
                    dpath = os.path.join(dirPath, "%s" % file)
                    if os.path.isdir(spath):
                        mergeFile(spath, dpath)
                    if os.path.isfile(spath):
                        shutil.copy(spath, dpath)
                        # os.system(f"xcopy {spath} {dpath} /y /e /i /h")

        # ==================删除9.5客户端，复制新版本===============================
        if chkEpoRlt and epobacRlt:
            delFile(os.path.abspath(os.path.join(dirPath, "..\\epolestar")))

            src = os.path.join(workDir, "epolestar")
            des = os.path.abspath(os.path.join(dirPath, "..\\epolestar"))
            os.system(f'xcopy "{src}" "{des}" /y /e /i /h')

        print("更新完成！")


if __name__ == '__main__':
    # main(sys.argv[1])
    main()
















