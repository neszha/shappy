import moment from "moment/moment.js"
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

    async getActivity(req, res) {
        const result = {
            homeLight: [], 
            gardenLight: [], 
            montionDetector: []            
        }
        const keys = await redis.keys('device-activity:*')
        for (const key of keys) {
            const keyData = key.replace('device-activity:', '')
            const dataString = await redis.get(key)
            if (dataString) result[keyData] = JSON.parse(dataString).reverse()
        }
        return res.json({
            success: true,
            data: result
        })
    },

    /**
     * Method: POST
     */
    async postActivity(req, res) {
        const {key, value} = req.body
        const logSizeLimit = 10
        let activities = []
        const redisKey = 'device-activity:' + key
        const redisData = await redis.get(redisKey)
        if (redisData) activities = JSON.parse(redisData)
        const logString =  `[${moment().format('L')} ${moment().format('LTS')}] ${value}`
        activities.push(logString)
        if(activities.length > logSizeLimit) {
            activities = activities.slice(activities.length - logSizeLimit, activities.length)
        }
        await redis.set(redisKey, JSON.stringify(activities))
        return res.json({success: true})
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
            }
        }
        await redis.set(deviceStateKey, JSON.stringify(deviceState))
        return res.json({
            success: true,
            data: deviceState
        })
    },

    /**
     * METHOD: DELETE
     */
    async deleteActivity(req, res) {
        const key = req.params.key
        await redis.del('device-activity:' + key)
        return res.json({success: true})
    }

}