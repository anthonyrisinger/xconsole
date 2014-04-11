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

    def __init__(self, controller):
        self.controller = controller
        #TODO:  hardcode by controller...?
        #       move to Controller?
        self.username = 'zwr'

        self.auth_player_name = self.username
        self.auth_session = (
            'token'
            ':5ada5cd545f847b0b02ed59990ba3028'
            ':3796104317d746fa92c0205a4dd57c30'
            )

        self.version_name = '1.6.4-Forge9.11.1.965'
        self.game_directory = os.path.expanduser(
            '~/clients/{0}/'.format(self.username),
            )
        self.game_assets = self.game_directory + 'assets/virtual/legacy/'
        self.game_versions = self.game_directory + 'versions/'
        self.game_libraries = self.game_directory + 'libraries/'
        self.tweak_class = 'cpw.mods.fml.common.launcher.FMLTweaker'

    @property
    def manager(self):
        return self.controller.manager

    def start(self):
        key = self.controller.key
        with open('/var/lib/minecraft/mc-1.6.4-args-new',mode='w') as fp:
            fp.write(self.cmdline)
        self.manager.title_map[key] = subprocess.Popen(
            args=self.cmdline.split('\0'),
            cwd=self.game_directory,
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
            '\0-Djava.library.path={self.game_versions}/'
                '{self.version_name}/{self.version_name}-LOCK'
            '\0-cp\0'
              #---------------------------------
                '{self.game_libraries}net/minecraftforge/'
                    'minecraftforge/9.11.1.965/'
                        'minecraftforge-9.11.1.965.jar'
                ':{self.game_libraries}net/minecraft/'
                    'launchwrapper/1.8/'
                        'launchwrapper-1.8.jar'
                ':{self.game_libraries}org/ow2/asm/'
                    'asm-all/4.1/'
                        'asm-all-4.1.jar'
                ':{self.game_libraries}org/scala-lang/'
                    'scala-library/2.10.2/'
                        'scala-library-2.10.2.jar'
                ':{self.game_libraries}org/scala-lang/'
                    'scala-compiler/2.10.2/'
                        'scala-compiler-2.10.2.jar'
                ':{self.game_libraries}lzma/'
                    'lzma/0.0.1/'
                        'lzma-0.0.1.jar'
                ':{self.game_libraries}net/sf/jopt-simple/'
                    'jopt-simple/4.5/'
                        'jopt-simple-4.5.jar'
                ':{self.game_libraries}com/paulscode/'
                    'codecjorbis/20101023/'
                        'codecjorbis-20101023.jar'
                ':{self.game_libraries}com/paulscode/'
                    'codecwav/20101023/'
                        'codecwav-20101023.jar'
                ':{self.game_libraries}com/paulscode/'
                    'libraryjavasound/20101123/'
                        'libraryjavasound-20101123.jar'
                ':{self.game_libraries}com/paulscode/'
                    'librarylwjglopenal/20100824/'
                        'librarylwjglopenal-20100824.jar'
                ':{self.game_libraries}com/paulscode/'
                    'soundsystem/20120107/'
                        'soundsystem-20120107.jar'
                ':{self.game_libraries}argo/'
                    'argo/2.25_fixed/'
                        'argo-2.25_fixed.jar'
                ':{self.game_libraries}org/bouncycastle/'
                    'bcprov-jdk15on/1.47/'
                        'bcprov-jdk15on-1.47.jar'
                ':{self.game_libraries}com/google/guava/'
                    'guava/14.0/'
                        'guava-14.0.jar'
                ':{self.game_libraries}org/apache/commons/'
                    'commons-lang3/3.1/'
                        'commons-lang3-3.1.jar'
                ':{self.game_libraries}commons-io/'
                    'commons-io/2.4/'
                        'commons-io-2.4.jar'
                ':{self.game_libraries}net/java/jinput/'
                    'jinput/2.0.5/'
                        'jinput-2.0.5.jar'
                ':{self.game_libraries}net/java/jutils/'
                    'jutils/1.0.0/'
                        'jutils-1.0.0.jar'
                ':{self.game_libraries}com/google/code/gson/'
                    'gson/2.2.2/'
                        'gson-2.2.2.jar'
                ':{self.game_libraries}org/lwjgl/lwjgl/'
                    'lwjgl/2.9.0/'
                        'lwjgl-2.9.0.jar'
                ':{self.game_libraries}org/lwjgl/lwjgl/'
                    'lwjgl_util/2.9.0/'
                        'lwjgl_util-2.9.0.jar'
                ':{self.game_versions}{self.version_name}/'
                        '{self.version_name}.jar'
            #---------------------------------
            '\0net.minecraft.launchwrapper.Launch'
            #---------------------------------
            '\0--session\0{self.auth_session}'
            '\0--version\0{self.version_name}'
            '\0--gameDir\0{self.game_directory}'
            '\0--assetsDir\0{self.game_assets}'
            '\0--tweakClass\0{self.tweak_class}'
        ).format(self=self)
