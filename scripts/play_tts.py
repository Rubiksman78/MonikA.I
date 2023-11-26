from IPython import display as ipd
import simpleaudio as sa
from scripts.utils import HiddenPrints
import torch

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def play_TTS(
    step,
    msg,
    play_obj,
    sampling_rate,
    tts_model,
    voice_samples,
    conditioning_latents,
    TTS_MODEL,
    VOICE_SAMPLE_COQUI,
    uni_chr_re
):
    if step > 0:
        play_obj.stop()
    msg_audio = msg.replace("\n", " ")
    msg_audio = msg_audio.replace("{i}", "")
    msg_audio = msg_audio.replace("{/i}", ".")
    msg_audio = msg_audio.replace("~", "!")
    msg_audio = uni_chr_re.sub(r'', msg_audio)
    with HiddenPrints():
        if TTS_MODEL == "Your TTS":
            audio = tts_model.tts(
                text=msg_audio,
                speaker_wav=f'coquiai_audios/{VOICE_SAMPLE_COQUI}',
                language='en'
            )
        elif TTS_MODEL == "Tortoise TTS":
            if device == "cuda":
                gen, _ = tts_model.tts_stream(
                        text=msg_audio,
                        k=1,
                        voice_samples=voice_samples,
                        conditioning_latents=conditioning_latents,
                        num_autoregressive_samples=8,
                        diffusion_iterations=20,
                        return_deterministic_state=True,
                        length_penalty=1.8,
                        max_mel_tokens=500,
                        cond_free_k=2,
                        top_p=0.85,
                        repetition_penalty=2.,
                    )
            else:
                gen = tts_model.tts(
                        text=msg_audio,
                        k=1,
                        voice_samples=voice_samples,
                        conditioning_latents=conditioning_latents,
                        num_autoregressive_samples=8,
                        length_penalty=1.8,
                        max_mel_tokens=500,
                        top_p=0.85,
                        repetition_penalty=2.,
                    )
            audio = gen.squeeze(0).cpu().numpy()
    audio = ipd.Audio(audio, rate=sampling_rate)
    play_obj = sa.play_buffer(audio.data, 1, 2, sampling_rate)
    return play_obj
