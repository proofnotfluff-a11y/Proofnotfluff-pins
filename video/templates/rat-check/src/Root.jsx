import {Composition} from 'remotion';
import {RatCheck} from './RatCheck.jsx';

// Duration, size and every element come from props.json (tools/video_render.py); the defaults only let the
// composition load without props.
const fallback = {fps: 30, width: 1080, height: 1920, seconds: 1, elements: [], captions: [], progress: null, drift: 0, fonts: {}};

export const Root = () => (
  <Composition
    id="RatCheck"
    component={RatCheck}
    defaultProps={fallback}
    fps={30}
    width={1080}
    height={1920}
    durationInFrames={30}
    calculateMetadata={({props}) => ({
      durationInFrames: Math.round(props.seconds * props.fps),
      fps: props.fps,
      width: props.width,
      height: props.height,
    })}
  />
);
