Vue.component('drawing-canvas', {
	props: ['drawable', 'path'],
	template: '<canvas width=256 height=256 @mousedown="onMouseDown" @mouseup="onMouseUp" @mouseout="onMouseUp" @mousemove="onMouseMove" />',
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
		draw() {
			const ctx = this.$el.getContext('2d');
			ctx.strokeStyle = 'black';

			ctx.clearRect(0, 0, this.$el.width, this.$el.height);

			ctx.beginPath();

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
		clear() {
			this.path_ = [];
			this.draw();
			this.$emit('clear');
		},
	},
});