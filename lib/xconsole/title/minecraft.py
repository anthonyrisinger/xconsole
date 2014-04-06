# coding: utf-8
"""
Minecraft

cdn: https://s3.amazonaws.com
key: https://authserver.mojang.com
lib: https://libraries.minecraft.net
mco: https://mcoapi.minecraft.net


  GET {cdn}/Minecraft.Download/launcher/launcher.pack.lzma
  <<<<<<<<<<<<<<<<<<< * 10101010 *


  GET {cdn}/Minecraft.Download/versions/versions.json
  <<<<<<<<<<<<<<<<<<< {
      "latest": {
          "snapshot": "14w06b",
          "release": "1.7.4"
          },
      "versions": [{
          "id": "14w06ab",
          "type": "snapshot",
          "time": "2014-02-06T18:30:42+01:00",
          "releaseTime": "2014-02-06T18:30:42+01:00
          }]
      }


  POST {key}/authenticate
  >>>>>>>>>>>>>>>>>>> {
      "clientToken": "00000000-0000-0000-0000-000000000000",
      "requestUser": true
      "username": "jsmith",
      "password": "jsmith",
      "agent": {
          "name": "Minecraft",
          "version": 1
          }
      }
  <<<<<<<<<<<<<<<<<<< {
      "clientToken": "00000000-0000-0000-0000-000000000000",
      "accessToken": "00000000000000000000000000000000",
      "user": {
          "id": "00000000000000000000000000000000"
          },
      "selectedProfile": {
          "id": "00000000000000000000000000000000"
          "name": "John Smith",
          }
      }


  POST {key}/refresh
  >>>>>>>>>>>>>>>>>>> {
      "clientToken": "00000000-0000-0000-0000-000000000000",
      "accessToken": "00000000000000000000000000000000",
      "requestUser": true
      }
  <<<<<<<<<<<<<<<<<<< {
      "clientToken": "00000000-0000-0000-0000-000000000000",
      "accessToken": "00000000000000000000000000000000",
      "user": {
          "id": "00000000000000000000000000000000"
          },
      "selectedProfile": {
          "id": "00000000000000000000000000000000"
          "name": "John Smith",
          },
      "availableProfiles": [{
          "id": "00000000000000000000000000000000",
          "name": "John Smith"
          }]
      }


  GET {cdn}/Minecraft.Download/versions/1.0.0/1.0.0.json
  <<<<<<<<<<<<<<<<<<< {...}


  GET {cdn}/Minecraft.Download/indexes/1.0.0.json
  <<<<<<<<<<<<<<<<<<< {...}


  GET {lib}/tv/twitch/twitch/5.12/twitch-5.12.jar
  <<<<<<<<<<<<<<<<<<< {...}


  GET {mco}/mco/available
  <<<<<<<<<<<<<<<<<<< {...}
"""

from __future__ import absolute_import
from __future__ import print_function

from pprint import pprint as pp
import sys
import os
import subprocess

import sys
import os


def get(controller):
    return Minecraft(controller)


class Minecraft(object):

    version = '1.7.4'

    def __init__(self, controller):
        self.controller = controller
        #TODO:  hardcode by controller...?
        #       move to Controller?
        self.username = 'emilyelese'
        self.uuid = 'db9e09c06ad64afcb1512c6118ba2e41'
        self.token = '8821254ece7d441ba2d041ad6c843acf'
        self.path = os.path.expanduser(
            '~/clients/{0}'.format(self.username),
            )
        self.path_version = self.path + '/versions'
        self.path_assets = self.path + '/assets'
        self.path_cp = self.path + '/libraries'

    @property
    def manager(self):
        return self.controller.manager

    def start(self):
        key = self.controller.key
        self.manager.title_map[key] = subprocess.Popen(
            args=self.cmdline.split('\0'),
            cwd=self.path,
            stdout=open(os.devnull, 'wb'),
            stderr=subprocess.STDOUT,
            )

    @property
    def cmdline(self):
        return (
            'java'
            '\0-server'
            '\0-Xms1024m'
            '\0-Xmx1024m'
            '\0-Xnoclassgc'
            '\0-XX:PermSize=256m'
            '\0-XX:NewRatio=3'
            '\0-XX:SurvivorRatio=3'
            '\0-XX:TargetSurvivorRatio=80'
            '\0-XX:MaxTenuringThreshold=8'
            '\0-XX:+UseParNewGC'
            '\0-XX:+UseConcMarkSweepGC'
            '\0-XX:MaxGCPauseMillis=10'
            '\0-XX:GCPauseIntervalMillis=50'
            '\0-XX:MaxGCMinorPauseMillis=7'
            '\0-XX:+ExplicitGCInvokesConcurrent'
            '\0-XX:+UseCMSInitiatingOccupancyOnly'
            '\0-XX:CMSInitiatingOccupancyFraction=60'
            '\0-XX:+BindGCTaskThreadsToCPUs'
            '\0-Dsun.java2d.opengl=true'
            '\0-Dsun.java2d.pmoffscreen=true'
            '\0-Djava.library.path={self.path_version}/'
                '{self.version}/{self.version}-LOCK'
            '\0-cp\0'
              #---------------------------------
                '{self.path_cp}/java3d/'
                    'vecmath/1.3.1/'
                        'vecmath-1.3.1.jar'
                ':{self.path_cp}/net/sf/trove4j/'
                    'trove4j/3.0.3/'
                        'trove4j-3.0.3.jar'
                ':{self.path_cp}/com/ibm/icu/'
                    'icu4j-core-mojang/51.2/'
                        'icu4j-core-mojang-51.2.jar'
                ':{self.path_cp}/net/sf/jopt-simple/'
                    'jopt-simple/4.5/'
                        'jopt-simple-4.5.jar'
                ':{self.path_cp}/com/paulscode/'
                    'codecjorbis/20101023/'
                        'codecjorbis-20101023.jar'
                ':{self.path_cp}/com/paulscode/'
                    'codecwav/20101023/'
                        'codecwav-20101023.jar'
                ':{self.path_cp}/com/paulscode/'
                    'libraryjavasound/20101123/'
                        'libraryjavasound-20101123.jar'
                ':{self.path_cp}/com/paulscode/'
                    'librarylwjglopenal/20100824/'
                        'librarylwjglopenal-20100824.jar'
                ':{self.path_cp}/com/paulscode/'
                    'soundsystem/20120107/'
                        'soundsystem-20120107.jar'
                ':{self.path_cp}/io/netty/'
                    'netty-all/4.0.10.Final/'
                        'netty-all-4.0.10.Final.jar'
                ':{self.path_cp}/com/google/guava/'
                    'guava/15.0/'
                        'guava-15.0.jar'
                ':{self.path_cp}/org/apache/commons/'
                    'commons-lang3/3.1/'
                        'commons-lang3-3.1.jar'
                ':{self.path_cp}/commons-io/'
                    'commons-io/2.4/'
                        'commons-io-2.4.jar'
                ':{self.path_cp}/net/java/jinput/'
                    'jinput/2.0.5/'
                        'jinput-2.0.5.jar'
                ':{self.path_cp}/net/java/jutils/'
                    'jutils/1.0.0/'
                        'jutils-1.0.0.jar'
                ':{self.path_cp}/com/google/code/gson/'
                    'gson/2.2.4/'
                        'gson-2.2.4.jar'
                ':{self.path_cp}/com/mojang/'
                    'authlib/1.2/'
                        'authlib-1.2.jar'
                ':{self.path_cp}/org/apache/logging/log4j/'
                    'log4j-api/2.0-beta9/'
                        'log4j-api-2.0-beta9.jar'
                ':{self.path_cp}/org/apache/logging/log4j/'
                    'log4j-core/2.0-beta9/'
                        'log4j-core-2.0-beta9.jar'
                ':{self.path_cp}/org/lwjgl/lwjgl/'
                    'lwjgl/2.9.1-nightly-20131120/'
                        'lwjgl-2.9.1-nightly-20131120.jar'
                ':{self.path_cp}/org/lwjgl/lwjgl/'
                    'lwjgl_util/2.9.1-nightly-20131120/'
                        'lwjgl_util-2.9.1-nightly-20131120.jar'
                ':{self.path_cp}/tv/twitch/'
                    'twitch/5.12/'
                        'twitch-5.12.jar'
                ':{self.path_version}/{self.version}/'
                        '{self.version}.jar'
            #---------------------------------
            '\0net.minecraft.client.main.Main'
            #---------------------------------
            '\0--username\0{self.username}'
            '\0--version\0{self.version}'
            '\0--gameDir\0{self.path}'
            '\0--assetsDir\0{self.path_assets}'
            '\0--assetIndex\0{self.version}'
            '\0--uuid\0{self.uuid}'
            '\0--accessToken\0{self.token}'
            '\0--userProperties\0{{}}'
            '\0--userType\0mojang'
        ).format(self=self)
