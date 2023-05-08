import redis from "./database/redis.db.js"

const deviceStateKey = 'device-state'

export default {
    /**
     * Method: GET
     */
    async getDeviceState(req, res) {
        const deviceStateJsonString = await redis.get(deviceStateKey)
        const deviceState = JSON.parse(deviceStateJsonString)
        return res.json({
            success: true,
            data: deviceState
        })
    },

    /**
     * Method: PUT
     */
    async updateDeviceState(req, res) {
        const deviceStateBody = req.body
        const updateType = req.query.updateType
        const deviceStateJsonString = await redis.get(deviceStateKey)
        const deviceState = JSON.parse(deviceStateJsonString) || {}
        const {homeLight, gardenLight, montionDetector} = deviceStateBody
        if (updateType === 'config') { // Update config state.
            if (homeLight) {
                deviceState.homeLight.auto = homeLight.auto
                deviceState.homeLight.sensitivity = homeLight.sensitivity
            }
            if (gardenLight) {
                deviceState.gardenLight.auto = gardenLight.auto
                deviceState.gardenLight.sensitivity = gardenLight.sensitivity
            }
            if (montionDetector) {
                deviceState.montionDetector.auto = montionDetector.auto
            }
        } else { // Update value state.
            if (homeLight) {
                deviceState.homeLight.isActive = homeLight.isActive
            }
            if (gardenLight) {
                deviceState.gardenLight.isActive = gardenLight.isActive
            }
            if (montionDetector) {
                deviceState.montionDetector.isActive = montionDetector.isActive
                console.log(montionDetector)
            }
        }
        await redis.set(deviceStateKey, JSON.stringify(deviceState))
        return res.json({
            success: true,
            data: deviceState
        })
    }

}