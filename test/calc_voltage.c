#include <stdio.h>

float toADC(float v)
{
    return (v * 4095.0f) / 3.3f;
}

int main()
{
    float R1;
    float f_R1 = 20000.0f;
    float f_R2 = 24000.0f;

    float highest = 0;
    float best = 0;

    for (R1 = 1000; R1 <= 100000; R1 += 100)
    {
        float v_unflexed = 3.3f * f_R1 / (R1 + f_R1);
        float v_flexed   = 3.3f * f_R2 / (R1 + f_R2);

        float adc_unflexed = toADC(v_unflexed);
        float adc_flexed   = toADC(v_flexed);

        float delta = adc_flexed - adc_unflexed;

        if (delta > highest)
        {
            highest = delta;
            best = R1;
        }

        printf("R1= %.0f | V_unflexed= %.4f | V_flexed= %.4f | ΔADC= %.2f\n",
               R1, v_unflexed, v_flexed, delta);
    }

    printf("\n-----> Best R1 = %.0f Ω\n", best);

    float v_u = 3.3f * f_R1 / (best + f_R1);
    float v_f = 3.3f * f_R2 / (best + f_R2);

    printf("Final:\n");
    printf("V_unflexed = %.4f V\n", v_u);
    printf("V_flexed   = %.4f V\n", v_f);
    printf("Delta ADC  = %.2f\n", toADC(v_f) - toADC(v_u));

    return 0;
}