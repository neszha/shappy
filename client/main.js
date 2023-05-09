const app = Vue.createApp({
    computed: {
        homeLight() {
            return this.deviceState?.homeLight || {
                auto: false,
                sensitivity: 255,
                isActive: false,
            }
        },

        gardenLight() {
            return this.deviceState?.gardenLight || {
                auto: false,
                sensitivity: 255,
                isActive: false,
            }
        },

        montionDetector() {
            return this.deviceState?.montionDetector || {
                auto: false,
                isActive: false,
            }
        },

        automaticGate() {
            return this.deviceState?.automaticGate || {
                auto: false,
                isActive: false,
            }
        }
    },

    methods: {
        /** API */
        getDeviceState() {
            const url = '/api/device/state?get=true'
            return axios.get(url).then(({data}) => {
                const deviceState = data.data
                this.deviceState = deviceState
            })
        },

        getDeviceActivity() {
            const url = '/api/device/activity'
            return axios.get(url).then(({data}) => {
                const activities = data.data
                this.activities = activities
            })
        },

        updateDeviceState() {
            const url = '/api/device/state?updateType=config'
            const body = this.deviceState
            return axios.put(url, body).catch(() => {})
        },

        async deleteActivity(key) {
            const url = '/api/device/activity/' + key
            await axios.delete(url)
            this.getDeviceActivity()
        },

        /** CONTROLS. */
        async sensitivityOnChange(event) {
            const key = event.target.getAttribute('name')
            const sensitivity = Number(event.target.value) || 0
            this.deviceState[key].sensitivity = sensitivity
            this.updateDeviceState()
        },

        async modeOnChange(key) {
            const data = this.deviceState[key]
            this.deviceState[key].auto = !data?.auto
            this.updateDeviceState()
        },

        gettingInterval() {
            setInterval(() => {
                this.getDeviceState()
                this.getDeviceActivity()
            }, 2000)
        }
    },

    async beforeMount() {
        await this.getDeviceState()
        await this.getDeviceActivity()
        this.gettingInterval()
    },

    mounted() {
        //
    },

    data() {
        return {
            deviceState: {
                homeLight: {},
                gerdenLight: {},
                montionDetector: {},
                automaticGate: {}
            },
            activities: {
                homeLight: [], 
                gardenLight: [], 
                montionDetector: [],
                automaticGate: []
            }
        };
    },
});

app.mount('#app');