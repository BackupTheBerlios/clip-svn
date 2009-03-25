class Crystal: QObject,FitObject {

%TypeHeaderCode
#include <crystal.h>
%End
    public:
        enum RotationAxisType {
            LabSystem,
            ReziprocalSpace,
            DirectSpace
        };
        
        Crystal(QObject* parent);
        ~Crystal();
        
        Crystal* copy() /Factory/;
%MethodCode        
        sipRes = new Crystal(*sipCpp);
%End        

        void generateReflections();
        void updateRotation();


        unsigned int reflectionCount();
        Reflection getReflection(unsigned int i);
        Reflection getClosestReflection(const Vec3D& normal);
        QList<Reflection>getReflectionList();

        Vec3D uvw2Real(const Vec3D&);
        Vec3D uvw2Real(int u, int v, int w);
        Vec3D hkl2Reziprocal(const Vec3D&);
        Vec3D hkl2Reziprocal(int h, int k, int l);

        Mat3D getRealOrientationMatrix() const;
        Mat3D getReziprocalOrientationMatrix() const;
        Mat3D getRotationMatrix() const;
        
        void calcEulerAngles(double &omega /Out/, double &chi /Out/, double &phi /Out/);
        void setEulerAngles(double omega, double chi, double phi);
        
        QList<Projector*> getConnectedProjectors();
        QString getSpacegroupSymbol() const;
        QList<int> getSpacegroupConstrains() const;
        
        Vec3D getRotationAxis() const;
        Vec3D getLabSystamRotationAxis() const;
        RotationAxisType getRotationAxisType() const;
        
        QList<double> getCell();
        void enableUpdate(bool b=true);
        // Functions for fitting parameters
        virtual double fitParameterValue(unsigned int n);
        virtual void fitParameterSetValue(unsigned int n, double val);
        virtual void fitParameterSetEnabled(unsigned int n, bool enable);        
    public slots:
        void addRotation(const Vec3D& axis, double angle);
        void addRotation(const Mat3D& M);
        void setRotation(const Mat3D& M);
        void setCell(double a, double b, double c, double alpha, double beta, double gamma);
        void setWavevectors(double lower, double upper);
        void addProjector(Projector*);
        void updateWavevectorsFromProjectors();
        void setSpacegroupSymbol(const QString& s);
        void setSpacegroupConstrains(QList<int> constrains);        
        void setRotationAxis(const Vec3D& axis, RotationAxisType type=LabSystem);

    signals:
        void cellChanged();
        void orientationChanged();
        void reflectionsUpdate();
        void rotationAxisChanged();
        void constrainsChanged();
        
};

