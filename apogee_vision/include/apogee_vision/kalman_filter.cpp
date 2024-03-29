#include "apogee_vision/KalmanFilter.h"

/////////////////////////////////////////////////////////////
//                      CONSTRUCTORS
/////////////////////////////////////////////////////////////
template <uint8_t StateDim, uint8_t MeasureDim>
KalmanFilter<StateDim, MeasureDim>::KalmanFilter(StateMatrix transition_matrix, StateMatrix process_noise_matrix, StateMatrix estimation_uncertainty_matrix, Eigen::Matrix<float, MeasureDim, StateDim> observation_matrix_,
            const StateVector &initial_state_guess, float initial_uncertainty_guess, float dt_, float acceleration_variance, float measurement_variance)
{
    // Set initial estimates
    state_estimate = initial_state_guess;
    state_transition = transition_matrix;
    process_noise = process_noise_matrix;
    estimation_uncertainty = estimation_uncertainty_matrix;
    observation_matrix = observation_matrix_;


    // Initialize measurement uncertainty matrix
    measurement_uncertainty = MeasureMatrix::Identity() * measurement_variance;
}

/////////////////////////////////////////////////////////////
//                      DESTRUCTOR
/////////////////////////////////////////////////////////////

template <uint8_t StateDim, uint8_t MeasureDim>
KalmanFilter<StateDim, MeasureDim>::~KalmanFilter() {}

/////////////////////////////////////////////////////////////
//                      PRIVATE FUNCTIONS
/////////////////////////////////////////////////////////////

/* @Brief - Updates the kalman gain, state estimate and estimation uncertainty based
*           on the latest measurement.
*
* @param[in] measurement - (x, y, z) position measurement
*                           aka Z in notation
*
* @return N/A
*/
template <uint8_t StateDim, uint8_t MeasureDim>
void KalmanFilter<StateDim, MeasureDim>::measurement_update(const MeasureVector &measurement)
{
    // Kalman gain update equation
    // K = P * H^T(HPH^T + R)^-1
    kalman_gain = estimation_uncertainty * observation_matrix.transpose() * 
            (observation_matrix * estimation_uncertainty * observation_matrix.transpose() +
            measurement_uncertainty).inverse();

    // State update equation
    // X = X + K(z - HX)

    // (z - HX) part
    innovation = measurement - observation_matrix * state_estimate;
    state_estimate = state_estimate + kalman_gain * innovation; 

    // Covariance update equation
    // P = (I - KH) * P * (I - KH)^T + KRK^T
    StateMatrix I_minus_KH = StateMatrix::Identity() - kalman_gain * observation_matrix;

    estimation_uncertainty = I_minus_KH * estimation_uncertainty * I_minus_KH.transpose() +
            kalman_gain * measurement_uncertainty * kalman_gain.transpose();
}

/* @Brief - Extrapolates state estimate and estimation uncertainty
*
* @return N/A
*/
template <uint8_t StateDim, uint8_t MeasureDim>
void KalmanFilter<StateDim, MeasureDim>::predict(void)
{
    // State extrapolation equation
    // X = FX
    state_estimate = state_transition * state_estimate;

    // Covariance extrapolation equation
    // P = FPF^T + Q
    estimation_uncertainty = state_transition * estimation_uncertainty * state_transition.transpose() +
            process_noise;
}

/////////////////////////////////////////////////////////////
//                      PUBLIC FUNCTIONS
/////////////////////////////////////////////////////////////
template <uint8_t StateDim, uint8_t MeasureDim>
void KalmanFilter<StateDim, MeasureDim>::step(const MeasureVector &measurement)
{
    measurement_update(measurement);

    predict();
}

template <uint8_t StateDim, uint8_t MeasureDim>
void KalmanFilter<StateDim, MeasureDim>::predict_state(StateMatrix prediction_transition, StateVector &predicted_state)
{
    predicted_state = prediction_transition * state_estimate;
}

template <uint8_t StateDim, uint8_t MeasureDim>
void KalmanFilter<StateDim, MeasureDim>::get_state(StateVector &state)
{
    state = state_estimate;

    // Testing reveals that the velocity is off exactly by a factor of 2
    // for each axis. Internally the position and acceleration is correct so heres 
    // a quick patch
    //state[1] *= 2;
    //state[4] *= 2;
    //state[7] *= 2;
}

template <uint8_t StateDim, uint8_t MeasureDim>
float KalmanFilter<StateDim, MeasureDim>::get_convergence(void)
{
    return abs(innovation.sum());
}