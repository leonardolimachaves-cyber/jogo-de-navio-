using UnityEngine;

public class SistemaSomNaval : MonoBehaviour
{
    [Header("Fontes de Áudio (AudioSources)")]
    public AudioSource somMotor;        // Coloque o áudio em Loop (repetição)
    public AudioSource somCanhoes;      // Para disparos
    public AudioSource somExplosoes;    // Para impactos e água

    [Header("Clipes de Áudio (Arquivos .wav ou .mp3)")]
    public AudioClip clipeDisparoCanhao;
    public AudioClip clipeImpactoAgua;
    public AudioClip clipeImpactoCasco;

    [Header("Configurações de Realismo")]
    public float pitchMinimoMotor = 0.8f;
    public float pitchMaximoMotor = 1.5f;

    // Chame esta função no Update() passando a velocidade atual do navio (de 0 a 1)
    public void AtualizarSomMotor(float porcentagemVelocidade)
    {
        if (somMotor != null)
        {
            // O ronco do motor fica mais grave parado e mais agudo/forte acelerando
            somMotor.pitch = Mathf.Lerp(pitchMinimoMotor, pitchMaximoMotor, porcentagemVelocidade);
        }
    }

    public void TocarSomDisparo()
    {
        if (somCanhoes != null && clipeDisparoCanhao != null)
        {
            // Muda levemente o tom (entre 0.9 e 1.1) para cada tiro soar único
            somCanhoes.pitch = Random.Range(0.9f, 1.1f);
            somCanhoes.PlayOneShot(clipeDisparoCanhao);
        }
    }

    // Toca o som no local exato onde o projétil caiu (na água ou no inimigo)
    public void TocarSomImpacto(Vector3 posicaoDoImpacto, bool acertouNavio)
    {
        AudioClip clipeEscolhido = acertouNavio ? clipeImpactoCasco : clipeImpactoAgua;

        if (clipeEscolhido != null)
        {
            // Cria um som 3D temporário exatamente na posição onde o tiro caiu
            AudioSource.PlayClipAtPoint(clipeEscolhido, posicaoDoImpacto, 1.0f);
        }
    }
}
