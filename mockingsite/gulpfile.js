// Include gulp
var gulp = require('gulp'); 

var $ = require('gulp-load-plugins')();

// Include Our Plugins
var jshint = require('gulp-jshint');
var sass = require('gulp-sass');
var concat = require('gulp-concat');
var uglify = require('gulp-uglify');
var rename = require('gulp-rename');
var mainBowerFiles = require('main-bower-files');
var streamqueue = require('streamqueue');
var useref = require('gulp-useref');
var gulpif = require('gulp-if');
var minifyInline = require('gulp-minify-inline-scripts');
var uglifyInline = require('gulp-uglify-inline');
var gutil = require('gulp-util');
var del = require('del')
var browserSync = require('browser-sync').create();
var reload = browserSync.reload;
var runSequence = require('run-sequence');


// Paths
var jsSrcPath = 'static/mocktest/scripts/*.js'
var imgSrcPath = 'static/mocktest/images/**/*'
var imgDestPath = 'static_prod/mocktest/images/'
var fontSrcPath = 'static/mocktest/fonts/**'
var fontDestPath = 'static_prod/mocktest/fonts/'
var templateSearchPath = '../mocktest/templates/'
var templateSrcPath = '../mocktest/templates/**/*.html'
var templateProdDestPath = '../mocktest/templates_prod/'
var sassSrcPath = ['static/mocktest/sass/*.scss', 'static/mocktest/sass/components/components.scss']
var assetsSearchPath = '{., static}'
var scriptsProdSrcPath = '../mocktest/templates_prod/static/mocktest/scripts/*.js'
var stylesProdSrcPath = '../mocktest/templates_prod/static/mocktest/styles/*.css'
var scriptsDestPath = 'static_prod/mocktest/scripts/'
var cssSrcPath = 'static/mocktest/css/*.css'
var cssDevDestPath = 'static/mocktest/styles/'
var cssProdDestPath = 'static_prod/mocktest/styles/'

var AUTOPREFIXER_BROWSERS = [
  'ie >= 10',
  'ie_mob >= 10',
  'ff >= 30',
  'chrome >= 34',
  'safari >= 7',
  'opera >= 23',
  'ios >= 7',
  'android >= 4.4',
  'bb >= 10'
];

// Lint Task
gulp.task('jshint', function() {
    return gulp.src(jsSrcPath)
        .pipe(jshint())
        .pipe(jshint.reporter('jshint-stylish'));
});


// Optimize images
gulp.task('images', function () {
  return gulp.src(imgSrcPath)
    .pipe($.imagemin({ //HACKED BY MAKING JPEGTRAN NOT WORK
      progressive: true,
      interlaced: true
    }))
    .pipe(gulp.dest(imgDestPath))
    .pipe($.size({title: 'images'}));
});


// Copy web fonts to dist
gulp.task('fonts', function () {
  return gulp.src([fontSrcPath])
    .pipe(gulp.dest(fontDestPath))
    .pipe($.size({title: 'fonts'}));
});

// Scan your HTML for assets & optimize them
gulp.task('html', function () {
  var assets = $.useref.assets({searchPath: assetsSearchPath});

  return gulp.src(templateSrcPath)
    .pipe(assets)
    // Concatenate and minify JavaScript
    .pipe($.if('*.js', $.uglify()))
    // Remove any unused CSS
    // Note: if not using the Style Guide, you can delete it from
    //       the next line to only include styles your project uses.
//    .pipe($.if('*.css', $.uncss({
//      html: [
//	  	templateSrcPath
//      ],
//      // CSS Selectors for UnCSS to ignore
//      ignore: [
//        /.navdrawer-container.open/,
//        /.app-bar.open/
//      ]
//    })))
    // Concatenate and minify styles
    .pipe($.if('*.css', $.csso()))
    .pipe(assets.restore())
    .pipe($.useref())
    // Update production Style Guide paths -- can be removed; I guess!
    //.pipe($.replace('components/components.css', 'components/main.min.css')) 
    // Minify any HTML
    //.pipe($.if('*.html', minifyInline())) //Can't minify inline javascript because of django template tags in them
    .pipe($.if('*.html', $.minifyHtml()))
    // Output files
    .pipe(gulp.dest(templateProdDestPath))
    .pipe($.size({title: 'html'}));
}); 

gulp.task('moveScripts', function() {
	return gulp.src(scriptsProdSrcPath)
		.pipe(gulp.dest(scriptsDestPath));
});


gulp.task('moveStyles', function() {
	return gulp.src(stylesProdSrcPath)
		.pipe(gulp.dest(cssProdDestPath));
});


gulp.task('fetchStyles', function () {
  // For best performance, don't add Sass partials to `gulp.src`
  return gulp.src(cssSrcPath)
    //.pipe($.sourcemaps.init()) //Including unmodified file symbols in the minified files
    .pipe($.autoprefixer({browsers: AUTOPREFIXER_BROWSERS})) // browser specific extensions
    //.pipe($.sourcemaps.write())
    .pipe(gulp.dest(cssDevDestPath))
    // Concatenate and minify styles --- We will do this using useref [So we are commenting it now]
    //.pipe($.if('*.css', $.csso())) // minify css files
    //.pipe(gulp.dest(cssProdDestPath))
    .pipe($.size({title: 'styles'}));
}); 

gulp.task('styles', function () {
  // For best performance, don't add Sass partials to `gulp.src`
  return gulp.src(sassSrcPath)
    //.pipe($.sourcemaps.init()) //Including unmodified file symbols in the minified files
    .pipe($.changed(cssDevDestPath, {extension: '.css'})) // Pick up just the changed files
    .pipe($.sass({
      precision: 10,
      onError: console.error.bind(console, 'Sass error:')
    })) // Compile sass to css files
    .pipe($.autoprefixer({browsers: AUTOPREFIXER_BROWSERS})) // browser specific extensions
    //.pipe($.sourcemaps.write())
    .pipe(gulp.dest(cssDevDestPath)) // write to a Dev location without minification
    // Concatenate and minify styles
    //.pipe($.if('*.css', $.csso())) // minify css files
    //.pipe(gulp.dest(cssProdDestPath))
    .pipe($.size({title: 'styles'}));
}); 


// Clean output directory
gulp.task('clean', del.bind(null, [
					'.tmp', 
					scriptsDestPath, 
					cssDevDestPath,
					cssProdDestPath,
					imgDestPath,
					fontDestPath,
					templateProdDestPath,
					scriptsProdSrcPath,
					stylesProdSrcPath
					], {dot: true, force: true}));



gulp.task ('run', ['styles', 'fetchStyles'], function() {
	browserSync.init ({
		proxy: 'crackit.com:8000',
		logPrefix: 'HIT'
	});

	gulp.watch([templateSrcPath], reload);
	gulp.watch([sassSrcPath], ['styles', reload]);
	gulp.watch([jsSrcPath], [reload]);
	gulp.watch([imgSrcPath], ['images', reload]);
	gulp.watch([cssSrcPath], ['fetchStyles', reload]);
});


gulp.task ('deploy', ['default'], function() {
	browserSync.init ({
		proxy: 'crackit.com:8000',
		logPrefix: 'HIT'
	});
});

gulp.task ('quick-deploy', [], function() {
	browserSync.init ({
		proxy: 'crackit.com:8000',
		logPrefix: 'HIT'
	});
});


// Concatenate & Minify JS
//gulp.task('scripts', function() {
//	return streamqueue({objectMode: true},
//			gulp.src('static_src/mocktest/scripts/*.js'),
//			gulp.src(mainBowerFiles({paths: 'static/'}))
//		)
//		.pipe(concat('all.js'))
//        .pipe(gulp.dest('static/mocktest/scripts/'))
//        .pipe(rename('all.min.js'))
//        .pipe(uglify())
//        .pipe(gulp.dest('static/mocktest/scripts/'));
//});


// Default Task -- Build Production files
gulp.task('default', ['clean'], function(cb) {
	runSequence(['styles', 'fetchStyles'], ['html', 'images', 'fonts'], ['moveScripts', 'moveStyles'], cb);
});
