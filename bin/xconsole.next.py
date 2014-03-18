#!/usr/bin/python3


# cdn: https://s3.amazonaws.com
# key: https://authserver.mojang.com
# lib: https://libraries.minecraft.net
# mco: https://mcoapi.minecraft.net
#
#
#   GET {cdn}/Minecraft.Download/launcher/launcher.pack.lzma
#   <<<<<<<<<<<<<<<<<<< * 10101010 *
#
#
#   GET {cdn}/Minecraft.Download/versions/versions.json
#   <<<<<<<<<<<<<<<<<<< {
#       "latest": {
#           "snapshot": "14w06b",
#           "release": "1.7.4"
#           },
#       "versions": [{
#           "id": "14w06ab",
#           "type": "snapshot",
#           "time": "2014-02-06T18:30:42+01:00",
#           "releaseTime": "2014-02-06T18:30:42+01:00
#           }]
#       }
#
#
#   POST {key}/authenticate
#   >>>>>>>>>>>>>>>>>>> {
#       "clientToken": "00000000-0000-0000-0000-000000000000",
#       "requestUser": true
#       "username": "jsmith",
#       "password": "jsmith",
#       "agent": {
#           "name": "Minecraft",
#           "version": 1
#           }
#       }
#   <<<<<<<<<<<<<<<<<<< {
#       "clientToken": "00000000-0000-0000-0000-000000000000",
#       "accessToken": "00000000000000000000000000000000",
#       "user": {
#           "id": "00000000000000000000000000000000"
#           },
#       "selectedProfile": {
#           "id": "00000000000000000000000000000000"
#           "name": "John Smith",
#           }
#       }
#
#
#   POST {key}/refresh
#   >>>>>>>>>>>>>>>>>>> {
#       "clientToken": "00000000-0000-0000-0000-000000000000",
#       "accessToken": "00000000000000000000000000000000",
#       "requestUser": true
#       }
#   <<<<<<<<<<<<<<<<<<< {
#       "clientToken": "00000000-0000-0000-0000-000000000000",
#       "accessToken": "00000000000000000000000000000000",
#       "user": {
#           "id": "00000000000000000000000000000000"
#           },
#       "selectedProfile": {
#           "id": "00000000000000000000000000000000"
#           "name": "John Smith",
#           },
#       "availableProfiles": [{
#           "id": "00000000000000000000000000000000",
#           "name": "John Smith"
#           }]
#       }
#
#
#   GET {cdn}/Minecraft.Download/versions/1.0.0/1.0.0.json
#   <<<<<<<<<<<<<<<<<<< {...}
#
#
#   GET {cdn}/Minecraft.Download/indexes/1.0.0.json
#   <<<<<<<<<<<<<<<<<<< {...}
#
#
#   GET {lib}/tv/twitch/twitch/5.12/twitch-5.12.jar
#   <<<<<<<<<<<<<<<<<<< {...}
#
#
#   GET {mco}/mco/available
#   <<<<<<<<<<<<<<<<<<< {...}


from pprint import pprint as pp
import sys
import os
import subprocess


if len(sys.argv) > 1 and sys.argv[1] == 'server':

    version = '1.6.4'
    base = '/var/lib/minecraft'

    cmdline = [
        '/usr/lib/jvm/java-7-openjdk/jre/bin/java',
        '-Xms1024m',
        '-Xmx1024m',
        '-XX:PermSize=256m',
        '-XX:NewRatio=3',
        '-XX:SurvivorRatio=3',
        '-XX:TargetSurvivorRatio=80',
        '-XX:MaxTenuringThreshold=8',
        '-XX:+UseParNewGC',
        '-XX:+UseConcMarkSweepGC',
        '-XX:MaxGCPauseMillis=10',
        '-XX:GCPauseIntervalMillis=50',
        '-XX:MaxGCMinorPauseMillis=7',
        '-XX:+ExplicitGCInvokesConcurrent',
        '-XX:+UseCMSInitiatingOccupancyOnly',
        '-XX:CMSInitiatingOccupancyFraction=60',
        '-XX:+BindGCTaskThreadsToCPUs',
        '-Xnoclassgc',
        '-server',
        '-Djava.library.path={0}/versions/{1}/{1}-natives'.format(
            base, version,
            ),
        '-Dsun.java2d.opengl=true',
        '-Dsun.java2d.pmoffscreen=true',
        '-cp',
        ':'.join(os.path.join(base, x) for x in [
            'libraries/net/sf/jopt-simple/jopt-simple/4.5/jopt-simple-4.5.jar',
            'libraries/com/paulscode/codecjorbis/20101023/codecjorbis-20101023.jar',
            'libraries/com/paulscode/codecwav/20101023/codecwav-20101023.jar',
            'libraries/com/paulscode/libraryjavasound/20101123/libraryjavasound-20101123.jar',
            'libraries/com/paulscode/librarylwjglopenal/20100824/librarylwjglopenal-20100824.jar',
            'libraries/com/paulscode/soundsystem/20120107/soundsystem-20120107.jar',
            'libraries/argo/argo/2.25_fixed/argo-2.25_fixed.jar',
            'libraries/org/bouncycastle/bcprov-jdk15on/1.47/bcprov-jdk15on-1.47.jar',
            'libraries/com/google/guava/guava/14.0/guava-14.0.jar',
            'libraries/org/apache/commons/commons-lang3/3.1/commons-lang3-3.1.jar',
            'libraries/commons-io/commons-io/2.4/commons-io-2.4.jar',
            'libraries/net/java/jinput/jinput/2.0.5/jinput-2.0.5.jar',
            'libraries/net/java/jutils/jutils/1.0.0/jutils-1.0.0.jar',
            'libraries/com/google/code/gson/gson/2.2.2/gson-2.2.2.jar',
            'libraries/org/lwjgl/lwjgl/lwjgl/2.9.0/lwjgl-2.9.0.jar',
            'libraries/org/lwjgl/lwjgl/lwjgl_util/2.9.0/lwjgl_util-2.9.0.jar',
            'versions/{0}/{0}.jar'.format(version),
            ]),
        'net.minecraft.server.MinecraftServer',
        ]

    cmdline = [
        '/usr/lib/jvm/java-7-openjdk/jre/bin/java',
        '-Xms1024m',
        '-Xmx1024m',
        '-XX:PermSize=256m',
        '-XX:NewRatio=3',
        '-XX:SurvivorRatio=3',
        '-XX:TargetSurvivorRatio=80',
        '-XX:MaxTenuringThreshold=8',
        '-XX:+UseParNewGC',
        '-XX:+UseConcMarkSweepGC',
        '-XX:MaxGCPauseMillis=10',
        '-XX:GCPauseIntervalMillis=50',
        '-XX:MaxGCMinorPauseMillis=7',
        '-XX:+ExplicitGCInvokesConcurrent',
        '-XX:+UseCMSInitiatingOccupancyOnly',
        '-XX:CMSInitiatingOccupancyFraction=60',
        '-XX:+BindGCTaskThreadsToCPUs',
        '-Xnoclassgc',
        '-server',
        '-jar',
        '{0}/minecraft_server.{1}.jar'.format(base, version),
        'nogui',
        ]

    pp(cmdline)
    os.chdir(base)
    pp(subprocess.call(cmdline))


'''
'--username',
'xtfxme',
'--session',
'token:{0}:{0}'.format('0'*32),
'--version',
'1.6.4',
'--gameDir',
base,
'--assetsDir',
'{0}/assets/virtual/legacy'.format(base),
'''
