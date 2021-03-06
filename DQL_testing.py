# TESTING the AI
import numpy as np
from keras.models import load_model
import DQL_environment
import matplotlib.pyplot as plt
from tqdm import tqdm


# Setting Parameters
number_actions = 7
direction_boundary = (number_actions - 1) / 2
temperature_step = 1.5
max_energy = direction_boundary * temperature_step
optimal_temperature = (20.0, 24.0)



tmin = 300
tmax = 800

for i in range(int(tmin/25), int(tmax/25)+1, 1):
    #Building the environment
    env = DQL_environment.Environment(optimal_temperature = optimal_temperature, initial_month = 0, initial_number_users = 20, initial_rate_data = 30, max_energy = max_energy)

    #Loading pre trained model (parameters: weights)
    # model_name = "modelBVSO800.h5"
    model_name = "modelBVSO" + str(i*25) + ".h5"
    model = load_model(model_name)
    
    
    #Inference mode
    train = False
    
    #1-Year simulation in Inference Mode
    env.train = train
    current_state, _, _ = env.observe()
    actions = []
    AI_T = []
    NO_AI_T = []
    FREE_T = []
    free_t = env.temperature_ai 
    time = []
    inside_AI = 0
    inside_NO_AI = 0
    mse_T_ai = []
    mse_T_noai = []
    E_AI = []
    E_NO_AI = []
    for timestep in tqdm(range(0, 1 * 30 * 24 * 60)):
    # for timestep in tqdm(range(0, 24*60*10)):
        q_values = model.predict(current_state)
        action = np.argmax(q_values[0])
        actions.append((action - direction_boundary) * temperature_step)
        if (action - direction_boundary < 0):
            direction = -1
        else:
            direction = 1
        energy_ai = abs(action - direction_boundary) * temperature_step
        next_state, reward, game_over = env.update_env(direction, energy_ai, int(timestep / (30*24*60)), timestep)
        
        ai_T = env.temperature_ai
        no_ai_T = env.temperature_noai
        AI_T.append(ai_T)
        NO_AI_T.append(no_ai_T)
        free_t += env.delta_intrinsic_temperature
        FREE_T.append(free_t)
        E_AI.append(env.total_energy_ai)
        E_NO_AI.append(env.total_energy_noai)
        time.append(timestep)
        current_state = next_state
        if ai_T >= optimal_temperature[0] and ai_T <= optimal_temperature[1]:
            inside_AI += 1
        if no_ai_T >= optimal_temperature[0] and no_ai_T <= optimal_temperature[1]:
            inside_NO_AI += 1
        # compute the mse from optimal t 21°
        mse_T_ai.append(env.temperature_ai - env.avg_optimal_temperature)              
        mse_T_noai.append(env.temperature_noai - env.avg_optimal_temperature)
    
        
        
    #Printing the result
    mse_T_ai = np.linalg.norm(mse_T_ai)
    mse_T_noai = np.linalg.norm(mse_T_noai)
    
    print(model_name)
    # print("Total Energy spent with an AI: {:.0f}".format(env.total_energy_ai))
    # print("Total Energy spent with no AI: {:.0f}".format(env.total_energy_noai))
    print("ENERGY SAVED: {:.0f} %".format((env.total_energy_noai - env.total_energy_ai) / env.total_energy_noai * 100))
    print("IN-BOUND: {:.0f} %".format((inside_AI - inside_NO_AI)/inside_AI * 100))
    # print("\nTemperature mse AI: {:.3f}".format(mse_T_ai/timestep))
    # print("Temperature mse No AI: {:.3f}".format(mse_T_noai/timestep))
    print("Failing: {:.2f}%\n\n".format(env.range_error/timestep*100))
    
    # Plotting the results
    plt.figure()
    plt.subplot(2,4,(1,4))
    plt.grid(True)
    # plt.plot(FREE_T)
    plt.plot(AI_T)
    plt.plot(NO_AI_T)
    plt.hlines(18, 0, len(time), colors='k', linestyles='dashed')
    plt.hlines(24, 0, len(time), colors='k', linestyles='dashed')
    plt.title('Server Temperature Comparison: ' + model_name )
    # plt.legend(('Free System', 'AKKA AI', 'No AI'))
    plt.legend(('AKKA AI', 'No AI'))
    plt.xlabel('time [min]')
    plt.ylabel('T_server [°C]')
    
    plt.subplot(2,4,5)
    plt.grid(True)
    plt.plot(actions)
    plt.title('Actions')
    plt.xlabel('time [min]')
    plt.ylabel('DT [°C]')
    
    plt.subplot(2,4,6)
    plt.grid(True)
    plt.plot(E_AI)
    plt.plot(E_NO_AI)
    plt.title('Energy Consumption')
    plt.legend(('AKKA AI', 'No AI'))
    plt.xlabel('time [min]')
    plt.ylabel('Energy')
    
    plt.subplot(2,4,7)
    plt.grid(True)
    plt.bar([0] , [inside_AI/len(time)])
    plt.bar([1] , [inside_NO_AI/len(time)])
    plt.xticks([0, 1], ('AKKA AI', 'No AI'))
    plt.title('InRange Time\n (the more the better)')
    plt.legend(('AKKA AI', 'No AI'))
    plt.ylabel('[%]')
    
    plt.subplot(2,4,8)
    plt.grid(True)
    plt.bar([0] , [env.total_energy_ai])
    plt.bar([1] , [env.total_energy_noai])
    plt.xticks([0, 1], ('AKKA AI', 'No AI'))
    plt.title('Total Energy Consumption\n (the less the better)')
    plt.legend(('AKKA AI', 'No AI'))
