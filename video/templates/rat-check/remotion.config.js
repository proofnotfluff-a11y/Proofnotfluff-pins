import {Config} from '@remotion/cli/config';

// Deterministic renders: one codec, one pixel format, the same JPEG quality for every frame.
Config.setVideoImageFormat('jpeg');
Config.setJpegQuality(92);
Config.setCodec('h264');
Config.setPixelFormat('yuv420p');
Config.setCrf(18);
Config.setOverwriteOutput(true);
