Vue.component('drawing-canvas', {
	props: ['drawable', 'path'],
	template: '<canvas width=256 height=256 @mousedown="onMouseDown" @mouseup="onMouseUp" @mouseout="onMouseOut" @mousemove="onMouseMove" />',
	data() {
		return {
			mouseDown: false,
			path_: this.path || [],
		};
	},
	computed: {
		rect() {
			return this.$el.getBoundingClientRect();
		},
	},
	mounted() {
		const canvas = this.$el;
		canvas.width = this.rect.width;
		canvas.height = this.rect.height;

		this.draw();
	},
	watch: {
		path(p) {
			this.mouseDown = false;
			this.path_ = p || [];
			this.draw();
		},
	},
	methods: {
		getPosByEvent(ev) {
			const rect = ev.target.getBoundingClientRect();
			return {
				x: (ev.clientX - rect.left) / rect.width,
				y: (ev.clientY - rect.top) / rect.height,
			};
		},
		posToCanvasPos(pos) {
			return {
				x: pos.x * this.rect.width,
				y: pos.y * this.rect.height,
			};
		},
		drawFrame() {
			const ctx = this.$el.getContext('2d');
			ctx.strokeStyle = '#eee';
			ctx.lineWidth = 4;

			ctx.beginPath();

			ctx.moveTo(this.$el.width*3/8, this.$el.height*2/8);
			ctx.lineTo(this.$el.width*2/8, this.$el.height*2/8);
			ctx.lineTo(this.$el.width*2/8, this.$el.height*3/8);

			ctx.moveTo(this.$el.width*5/8, this.$el.height*2/8);
			ctx.lineTo(this.$el.width*6/8, this.$el.height*2/8);
			ctx.lineTo(this.$el.width*6/8, this.$el.height*3/8);

			ctx.moveTo(this.$el.width*3/8, this.$el.height*6/8);
			ctx.lineTo(this.$el.width*2/8, this.$el.height*6/8);
			ctx.lineTo(this.$el.width*2/8, this.$el.height*5/8);

			ctx.moveTo(this.$el.width*5/8, this.$el.height*6/8);
			ctx.lineTo(this.$el.width*6/8, this.$el.height*6/8);
			ctx.lineTo(this.$el.width*6/8, this.$el.height*5/8);

			ctx.moveTo(this.$el.width*7/16, this.$el.height/2);
			ctx.lineTo(this.$el.width*9/16, this.$el.height/2);

			ctx.moveTo(this.$el.width/2, this.$el.height*7/16);
			ctx.lineTo(this.$el.width/2, this.$el.height*9/16);

			ctx.stroke();
		},
		draw() {
			const ctx = this.$el.getContext('2d');
			ctx.clearRect(0, 0, this.$el.width, this.$el.height);

			this.drawFrame();

			ctx.strokeStyle = 'black';
			ctx.lineWidth = 2;
			ctx.beginPath();

			ctx.moveTo(0, 0);

			if (this.path_.length > 0) {
				const startPos = this.posToCanvasPos(this.path_[0]);
				ctx.moveTo(startPos.x, startPos.y);

				this.path_.slice(1).forEach(p => {
					p = this.posToCanvasPos(p);
					ctx.lineTo(p.x, p.y);
				});

				ctx.stroke();
			}
		},
		onMouseDown(ev) {
			if (this.drawable) {
				this.mouseDown = true;

				const pos = this.getPosByEvent(ev);
				this.path_ = [pos];

				this.draw();

				this.$emit('start-draw', this.path_);
				this.$emit('update:path', this.path_);
			}
		},
		onMouseUp(ev) {
			if (this.mouseDown) {
				this.mouseDown = false;

				const pos = this.getPosByEvent(ev);
				this.path_.push(pos);

				this.draw();

				this.$emit('end-draw', this.path_);
				this.$emit('update:path', this.path_);
			}
		},
		onMouseMove(ev) {
			if (this.mouseDown) {
				const pos = this.getPosByEvent(ev);
				this.path_.push(pos);

				this.draw();

				this.$emit('update:path', this.path_);
			}
		},
		onMouseOut(ev) {
			if (this.mouseDown) {
				this.clear();
			}
		},
		clear() {
            this.mouseDown = false;
			this.path_ = [];
			this.draw();
			this.$emit('clear');
		},
	},
});


const vm = new Vue({
	el: 'main',
	data: {
		text: 'loading...',
		path: null,
		characters: 'あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわん',
	},
	mounted() {
		this.setup();
	},
	methods: {
		setup() {
            while (true) {
                const text = this.characters[Math.floor(Math.random()*this.characters.length)];
                if (text !== this.text) {
                    this.text = text;
                    break;
                }
            }
            this.loadExample();
		},
        loadExample() {
            axios.get('/example', {params: {text: this.text}})
                .then(res => {
                    this.path = res.data.map(p => ({x: p[0], y: p[1]}));
                })
                .catch(() => {
                    this.path = null;
                })
        },
		endDraw(path) {
            axios.post('/store', {
                text: this.text,
                path: path.map(p => [p.x, p.y]),
            }).catch(console.error);
			this.setup();
		},
	},
});
